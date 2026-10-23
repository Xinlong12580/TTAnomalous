import json

with open("Datasets_background_v15.json", "r") as f:
    dataset_json = json.load(f)["2024"]
with open("Xsections_background_old.json", "r") as f:
    old_xsec_json = json.load(f)


new_xsec_json = {}

for process in dataset_json:
    new_xsec_json[process] = {}
    for subprocess in dataset_json[process]:
        new_xsec_json[process][subprocess] = ""
        if process in old_xsec_json:
            if subprocess in old_xsec_json[process]:
                new_xsec_json[process][subprocess] = old_xsec_json[process][subprocess]

with open("Xsections_background.json", "w") as f:
    json.dump(new_xsec_json, f, indent = 4)
