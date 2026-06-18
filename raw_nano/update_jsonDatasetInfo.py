import json
import ROOT

with open('Datasets_background.json', 'r') as file:
    dataset_json = json.load(file)

info_json = {}
with open("datasetInfo.txt", "r") as f:
    f.seek(0)
    lines = f.readlines()
    lines = [line.strip().split() for line in lines]
    for line in lines:
        info_json.setdefault(f"{line[0]}", {}).setdefault(f"{line[1]}", {}).setdefault(f"{line[2]}", {})["sumEventCount"] = int(float(line[3]))
        info_json.setdefault(f"{line[0]}", {}).setdefault(f"{line[1]}", {}).setdefault(f"{line[2]}", {})["sumWeight"] = float(line[4])
    
for year in dataset_json:
    for process in dataset_json[year]:
        for subprocess in dataset_json[year][process]:
            sumEventCount = -1
            sumWeight = -1
            if (year in info_json) and (process in info_json[year]) and (subprocess in info_json[year][process]):
                sumEventCount = info_json[year][process][subprocess]["sumEventCount"]
                sumWeight = info_json[year][process][subprocess]["sumWeight"]
            print(f"{year} {process} {subprocess} {sumEventCount} {sumWeight}")
            dataset_json[year][process][subprocess]["sumEventCount"] = sumEventCount
            dataset_json[year][process][subprocess]["sumWeight"] = sumWeight

 
#with open('Datasets_background.json', 'w') as file:
with open('test.json', 'w') as file:
    dataset_json = json.dump(dataset_json, file, indent = 4)
