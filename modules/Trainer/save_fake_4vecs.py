import ROOT
import numpy as np
import json
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
#files = files[:1]

dataset = {"weight_All__nominal": [], "Mass_GJ": [], "Pt_GJ": [], "Eta_GJ": [], "Phi_GJ":[]}
for f in files:
    print(f)
    rdf = ROOT.RDataFrame("Events", f)
    if (rdf.Count().GetValue() < 1): continue
    _dataset = rdf.AsNumpy(columns = ["weight_All__nominal", "Mass_GJ", "Pt_GJ", "Eta_GJ", "Phi_GJ"])     
    for key in _dataset:
        print(key)
        _dataset[key] = [float(value) for value in _dataset[key]]
        dataset[key] += _dataset[key]

#print(type(dataset))
#print(dataset)
n_fakes = 10
for i in range(n_fakes):
    dataset[f"Mass_AFJ_{i}"] = dataset[f"Mass_GJ"]
    dataset[f"Pt_AFJ_{i}"] = dataset[f"Pt_GJ"]
    dataset[f"Eta_AFJ_{i}"] = dataset[f"Eta_GJ"]
    dataset[f"Phi_AFJ_{i}"] = dataset[f"Phi_GJ"]

with open("fake_4vecs.txt", "w") as f:
    json.dump(dataset, f)
