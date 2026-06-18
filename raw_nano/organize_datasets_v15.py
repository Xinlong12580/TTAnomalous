import json
from pathlib import Path
years = ["2022", "2022EE", "2023", "2023BPix", "2024"]
BKG_process = {"MC_TTBarJets":["TTto4Q", "TTtoLNu2Q", "TTto2L2Nu"], "MC_QCDJets": ["QCD-4Jets_HT-100to200", "QCD-4Jets_HT-200to400", "QCD-4Jets_HT-400to600", "QCD-4Jets_HT-600to800", "QCD-4Jets_HT-800to1000", "QCD-4Jets_HT-1000to1200", "QCD-4Jets_HT-1200to1500", "QCD-4Jets_HT-1500to2000", "QCD-4Jets_HT-2000"], "MC_TTHJets":["TTH-Hto2B"] }
BKG_json = {}
for year in years:
    BKG_json[year] = {}
    for process in BKG_process:
        BKG_json[year][process] = {}
        for subprocess in BKG_process[process]:
            BKG_json[year][process][subprocess] = ""
for process in BKG_process:
    with open(f"{process}_base.txt", "r") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        print(line)
        if "Par" not in line and "ext" not in line and "Fil" not in line:
            for year in years:
                if year[2:] + "Nano" in line or year[2:] + "Mini" in line:
                    for subprocess in BKG_process[process]:
                        if subprocess in line:
                            BKG_json[year][process][subprocess] = line
                            break
                    break
    f2024_path = Path(f"{process}_2024.txt")
    if not f2024_path.exists():
        continue
    with open(f"{process}_2024.txt", "r") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        print(line)
        #if "Par" not in line and "ext" not in line and "Fil" not in line:
        if  "ext" not in line and "Fil" not in line:
            for subprocess in BKG_process[process]:
                _subprocess = subprocess
                if process == "MC_QCDJets":
                    _subprocess = subprocess[10:]
                if _subprocess in line:
                    BKG_json["2024"][process][subprocess] = line
                    break
print(BKG_json)

with open("Datasets_background_v15.json", "w") as f:
    json.dump(BKG_json, f, indent = 4)

years = ["2022", "2022EE", "2023", "2023BPix", "2024"]
data_eras = {"2022" : ["C", "D"], "2022EE": ["E", "F", "G"], "2023": ["C"], "2023BPix" : ["D"], "2024": ["C", "D", "E", "F", "G", "H", "I"]}
Data_json = {}
for year in years:
    Data_json[year] = {}
    Data_json[year]["Data"] = {}
with open(f"Data_2022and2023.txt", "r") as f:
    lines = f.readlines()
for line in lines:
    line = line.strip()
    print(line)
    for year in years:
        for era in data_eras[year]:
            if year[:4] + era in line:
                Data_json[year]["Data"][line[1:].replace("/", "__")] = line
                break

with open(f"Data_2024.txt", "r") as f:
    lines = f.readlines()
for line in lines:
    line = line.strip()
    print(line)
    for era in data_eras["2024"]:
        if "2024" + era in line:
            Data_json["2024"]["Data"][line[1:].replace("/", "__")] = line
            break
print(Data_json)

print(Data_json)

with open("Datasets_data_v15.json", "w") as f:
    json.dump(Data_json, f, indent = 4)


exit()
years = ["2022", "2022EE", "2023", "2023BPix", "2024"]
Signal_json = {}
for year in years:
    Signal_json[year] = {}
    Signal_json[year]["SignalMC_XHY4b"] = {}
with open(f"SignalMC_XHY4b_2024.txt", "r") as f:
    lines = f.readlines()
for line in lines:
    line = line.strip()
    print(line)
    subprocess = line[line.find("MX-") : line.find("_TuneCP5")].replace("-MY", "_MY")
    Signal_json["2024"]["SignalMC_XHY4b"][subprocess] = line
print(Signal_json)

with open("Datasets_signal_v15.json", "w") as f:
    json.dump(Signal_json, f, indent = 4)
