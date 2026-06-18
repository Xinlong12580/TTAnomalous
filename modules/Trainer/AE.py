import numpy as np
import torch 
import torch.nn as nn
from torch.utils.data import TensorDataset, Dataset, DataLoader, random_split
import json
import matplotlib.pyplot as plt

class dataset(Dataset):
    def __init__(self, inputs):
        self.inputs = torch.as_tensor(inputs, dtype = torch.float32)
        self.outputs = torch.as_tensor(inputs, dtype = torch.float32)

class AE(nn.Module):
    def __init__(self, input_dim, hidden_dims, embedding_dim, activation=nn.ReLU, dropout = 0 ):
        super().__init__()
        layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims : #encoder
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(activation)
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            prev_dim = hidden_dim
        self.encoder = nn.Sequential(*layers)

        layers = []
        layers.append(nn.Linear(prev_dim, embedding_dim)) #embedding layer
        layers.append(nn.BatchNorm1d(embedding_dim))
        layers.append(activation)

        self.embedder = nn.Sequential(*layers)

        prev_dim = embedding_dim

        layers = []
        for hidden_dim in hidden_dims[::-1] : #decoder
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(activation)
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            prev_dim = hidden_dim

        layers.append(nn.Linear(prev_dim, input_dim))
        self.decoder = nn.Sequential(*layers)
        print(self.encoder)
        print(self.embedder)
        print(self.decoder)
        
    def forward(self, inputs):
        encoding = self.encoder(inputs)
        embedding = self.embedder(encoding)
        decoding = self.decoder(embedding)
        return decoding, embedding

    def loss_function(self, prediction, target):
        return nn.functional.mse_loss(prediction, target)

    def save(self, path):
        torch.save(self.state_dict(), path)
    
    def load(self, path, device = "cpu"):
        self.load_state_dict(torch.load(path, map_location = device) )
        self.to(device)
        self.eval()


def trainer(model, dataloader, optimizer, device = "cpu"):
    model.train()
    total_loss = 0.
    n_samples = 0.
    for inputs_batch  in dataloader:
        inputs_batch = inputs_batch[0].to(device)
        prediction, embedding = model(inputs_batch)
        loss = model.loss_function(prediction, inputs_batch)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        batch_size = inputs_batch.size(0)
        total_loss = loss.item() * batch_size
        n_samples += batch_size
    return total_loss/ n_samples


def evaluator(model, dataloader, device = "cpu"):
    model.eval()
    total_loss = 0.
    n_samples = 0.
    with torch.no_grad():
        for inputs_batch  in dataloader:
            inputs_batch = inputs_batch[0].to(device)
            prediction, embedding = model(inputs_batch)
            loss = model.loss_function(prediction, inputs_batch)
            batch_size = inputs_batch.size(0)
            total_loss = loss.item() * batch_size
            n_samples += batch_size
    return total_loss/ n_samples

def calculator(model, inputs_batch, device = "cpu"):
    model.eval()
    with torch.no_grad():
        inputs_batch = inputs_batch.to(device)
        prediction, embedding = model(inputs_batch)
    return prediction, embedding


def normalize(tensor, mean, stdev, epsilon = 1e-8):
    return (tensor - mean ) / (stdev + epsilon )

def denormalize(tensor, mean, stdev, epsilon = 1e-8):
    return tensor * (stdev + epsilon ) + mean
    
if __name__ == "__main__":
    with open("fake_4vecs.txt", "r") as f:
        fake_4vecs = json.load(f)

    input_list = []
    for i in range(10):
        for variable in ["Mass_AFJ", "Pt_AFJ", "Eta_AFJ", "Phi_AFJ"]:
            input_list.append(np.asarray(fake_4vecs[variable + f"_{i}" ]))
    input_list = np.asarray(input_list)
    print(input_list.T.shape)
    
    #Input = torch.tensor( np.concatenate(input_list, axis = 1), dtype = torch.float32)
    Input = torch.tensor( input_list.T, dtype = torch.float32)
    N = Input.shape[0]
    
    train_fraction = 0.7
    val_fraction = 0.2
    n_train = int(N * train_fraction)
    n_val = int(N * val_fraction)
    
    generator = torch.Generator().manual_seed(42)
    indices = torch.randperm(N, generator = generator)
    
    train_indices = indices[:n_train]
    val_indices = indices[n_train:n_train + n_val]
    test_indices = indices[n_train+n_val:]
    
    train_Input = Input[train_indices]
    val_Input = Input[val_indices]
    test_Input = Input[test_indices]
    
    train_mean = train_Input.mean(dim = 0, keepdim = True) 
    train_std = train_Input.std(dim = 0, keepdim = True, correction = 0)

    train_Input_norm = normalize(train_Input, train_mean, train_std) 
    print(type(train_Input_norm))
    val_Input_norm = normalize(val_Input, train_mean, train_std) 
    test_Input_norm = normalize(test_Input, train_mean, train_std) 


    train_dataset = TensorDataset(train_Input_norm)
    val_dataset = TensorDataset(val_Input_norm)
    test_dataset = TensorDataset(test_Input_norm)
     

    train_dataloader = DataLoader(train_dataset, batch_size = 64, shuffle = True) 
    val_dataloader = DataLoader(val_dataset, batch_size = 64, shuffle = False)
    test_dataloader = DataLoader(test_dataset, batch_size = 100000, shuffle = False)
    
    device  = "cuda" if torch.cuda.is_available() else "cpu" 
    model = AE( 40, (64, 32, 8), 4, nn.ReLU(), 0.1).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr = 1e-3)
    n_epoches = 2
    for epoch in range(n_epoches):
        train_loss = trainer(model, train_dataloader, optimizer, device)
        print(f"epoch: {epoch + 1} | train loss: {train_loss}")
        val_loss = evaluator(model, val_dataloader, device)
        print(f"epoch: {epoch + 1} | val loss: {val_loss}")

        
    model.save("checkpoint/test.pt")
    for inputs_batch in test_dataloader:
        inputs_batch = inputs_batch[0]
        outputs_batch, embedding = calculator(model, inputs_batch, device)
        
        inputs_batch = denormalize(inputs_batch , train_mean, train_std)
        outputs_batch = denormalize(outputs_batch , train_mean, train_std)
        print(inputs_batch) 
        print(outputs_batch) 
        print(embedding) 
        pt_inputs = inputs_batch[:,1].detach().cpu().numpy()
        pt_outputs = outputs_batch[:,1].detach().cpu().numpy()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.hist(pt_inputs, label = "input", facecolor = "none", edgecolor = "red")
        ax.hist(pt_outputs, label = "output", facecolor = "none", edgecolor = "blue")
        ax.legend()
        ax.set_title("pt distribution of AE inputs and outputs")
        ax.set_xlabel("pt[GeV]")
        ax.set_ylabel("count")
        #fig.savefig("dis_pt.png")
        fig.savefig("after_training_dis_pt.png")
        break     
        
    
    
