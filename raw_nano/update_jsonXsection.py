import json

with open('Datasets_background.json', 'r') as file:
    dataset_json = json.load(file)
with open('Xsections_background.json', 'r') as file:
    Xsection_json = json.load(file)

for year in dataset_json:
    for process in dataset_json[year]:
        for subprocess in dataset_json[year][process]:
            Xsection = Xsection_json[process][subprocess]
            print(f"{subprocess} {Xsection}")
            dataset_json[year][process][subprocess]["Xsection"] = Xsection

 
with open('Datasets_background.json', 'w') as file:
    dataset_json = json.dump(dataset_json, file, indent = 4)
