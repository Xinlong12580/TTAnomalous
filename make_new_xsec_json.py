import json

with open("Datasets_background_v15.json", "r") as f:
    dataset_json = json.load(f)
with open("Xsections_background.json", "r") as f:
    old_xsec_json = json.load(f)
