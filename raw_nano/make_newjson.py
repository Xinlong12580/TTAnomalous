import json

with open('datasets_XHY4b_Base.json', 'r') as file:
    ori_json = json.load(file)
new_json = {}

for year in ori_json:
    year_json = ori_json[year] 
    new_year_json = {}
    for dataset in year_json:
        if dataset == "Data":
            continue
        subsets = year_json[dataset]
        new_dataset_json = {}
        for subset in subsets:
            #print(f"{year} {dataset} {subset}")
            subprocess = subset[1 : subset.find("_Tune")]
            print(subprocess)
            new_subprocess_json = {"Dataset" : subset}
            new_dataset_json[subprocess] = new_subprocess_json
        new_year_json[dataset] = new_dataset_json
    new_json[year] = new_year_json

with open("Datasets_background.json", "w") as file:
    json.dump(new_json, file, indent=4)


with open('datasets_XHY4b_Base.json', 'r') as file:
    ori_json = json.load(file)
new_json = {}

for year in ori_json:
    year_json = ori_json[year] 
    new_year_json = {}
    for dataset in year_json:
        if dataset != "Data":
            continue
        subsets = year_json[dataset]
        new_dataset_json = {}
        for subset in subsets:
            #print(f"{year} {dataset} {subset}")
            subprocess = subset[1 : subset.find("_Tune")]
            subprocess = subset.replace("/", "__")[2:]
            #subprocess = "Data"
            print(subprocess)
            new_subprocess_json = {"Dataset" : subset}
            new_dataset_json[subprocess] = new_subprocess_json
        new_year_json[dataset] = new_dataset_json
    new_json[year] = new_year_json

with open("Datasets_data.json", "w") as file:
    json.dump(new_json, file, indent=4)


with open('signal_XHY4b_Base.json', 'r') as file:
    ori_json = json.load(file)
new_json = {}

for year in ori_json:
    year_json = ori_json[year] 
    new_year_json = {}
    for dataset in year_json:
        subsets = year_json[dataset]
        new_dataset_json = {}
        for subset in subsets:
            #print(f"{year} {dataset} {subset}")
            subprocess = subset[subset.find("MX-") : subset.find("_Tune")]
            subprocess = subprocess.replace("-MY", "_MY")
            print(subprocess)
            new_subprocess_json = {"Dataset" : subset}
            new_dataset_json[subprocess] = new_subprocess_json
        new_year_json[dataset] = new_dataset_json
    new_json[year] = new_year_json

with open("Datasets_signal.json", "w") as file:
    json.dump(new_json, file, indent=4)
