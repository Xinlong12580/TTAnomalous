import ROOT
import numpy as np
import json
import uproot
import os
import sys
DIR_TOP = os.environ["ANA_TOP"]
sys.path.append(DIR_TOP)
from TTAnomalous_Helper import *
files = []
with open(DIR_TOP + "/outputList/output_quick_selection.txt", "r") as f:
    for line in f.readlines():
        if "Template" not in line and "RegCon" in line and "JetMET" in line:
            files.append(line.strip())
            print(line.strip())


dataset = uproot.concatenate(
    [f"{f}:Events" for f in files],
    expressions=["weight_All__nominal", "Mass_GJ", "Pt_GJ", "Eta_GJ", "Phi_GJ"],
    library="np",
)

for key in dataset:
    print(key)
    dataset[key] = list(dataset[key])
n_fakes = 10
for i in range(n_fakes):
    dataset[f"Mass_AFJ_{i}"] = dataset[f"Mass_GJ"]
    dataset[f"Pt_AFJ_{i}"] = dataset[f"Pt_GJ"]
    dataset[f"Eta_AFJ_{i}"] = dataset[f"Eta_GJ"]
    dataset[f"Phi_AFJ_{i}"] = dataset[f"Phi_GJ"]

with open("fake_4vecs.txt", "w") as f:
    json.dump(dataset, f)
