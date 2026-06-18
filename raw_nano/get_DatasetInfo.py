import json
import ROOT
import os
def get_InfoSum(file_name, columns):
    nTotal = 0
    with open (file_name, "r") as f:
        lines = f.readlines()
        runs = ROOT.RDataFrame("Runs", lines)
        nTotals = []
        for column in columns:
            nTotal = runs.Sum(column).GetValue()
            nTotals.append(nTotal)
    return nTotals

        
def get_InfoSum_v2(file_name):
    genEventCount = 0
    genEventSumw = 0
    with open (file_name, "r") as f:
        lines = f.readlines()
        runs = ROOT.RDataFrame("Runs", lines)
        for line in lines:
            line = line.strip()
            try:
                root_file = ROOT.TFile.Open( line)
            except Exception as e:
                with open("BAD_ROOT_FILES.txt", "a") as badf:
                    badf.write(f"{file_name} {line}\n")
            else:
                runs = root_file.Runs 
                for entry in runs:
                    genEventCount += runs.genEventCount
                    genEventSumw += runs.genEventSumw 
    return [genEventCount, genEventSumw]

with open('Datasets_background.json', 'r') as file:
    dataset_json = json.load(file)

with open("datasetInfo.txt", "a+") as f:
    f.seek(0)
    lines = f.readlines()
    print(lines[0])
    lines =[line.strip().split() for line in lines]
    #print(lines[0])
    lines_head = [line[0:3] for line in lines]
    
    for year in dataset_json:
        for process in dataset_json[year]:
            for subprocess in dataset_json[year][process]:
                if [year, process, subprocess] in lines_head:
                    print(f"INFO OF {year} {process} {subprocess} ALREADY EXISTS")
                    continue
                file_name = f"files/{year}__{process}__{subprocess}.txt"
                if not os.path.exists(file_name):
                    print(f"{file_name} DOESN't EXIST")
                    continue
                print(f"GETTING INFO FROM {file_name}")
                #nTotals = get_InfoSum(file_name, ["genEventCount", "genEventSumw"])
                nTotals = get_InfoSum_v2(file_name)
                sumEventCount = nTotals[0]
                sumWeight = nTotals[1]

                print(f"{year} {process} {subprocess} {sumEventCount} {sumWeight}")
                f.write(f"{year} {process} {subprocess} {sumEventCount} {sumWeight}\n")
                f.flush()        
                #dataset_json[year][process][subprocess]["sumEventCount"] = sumEventCount
                #dataset_json[year][process][subprocess]["sumWeight"] = sumWeight

 
#with open('Datasets_background.json', 'w') as file:
#    dataset_json = json.dump(dataset_json, file, indent = 4)
