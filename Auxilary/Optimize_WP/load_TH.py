import ROOT
import os
import sys
import array
import json
import pickle as pkl
DIR_TOP = os.environ["ANA_TOP"]
sys.path.append(DIR_TOP)
from TTAnomalous_Helper import *

processes = {"MC_TTBarJets":["*"], "MC_TTHJets":["*"]}
bins = {"Score_FatJet_XbbVSQCD_AFJ": array.array("d", np.linspace(0, 1, 101) ), "Score_FatJet_OneminusQCD_AFJ": array.array("d", np.linspace(0, 1, 101) )}
years = ["2024"]

with open(DIR_TOP + "/raw_nano/Xsections_background.json") as f:
    Xsec_json = json.load(f)

with open(DIR_TOP + "outputList/output_quick_selection.txt", "r") as f:
    files = [line.strip() for line in f.readlines() if "Template" not in line and "RegSig" in line and "Data" not in line and "/Muon" in line]

output_pkl = "hists_pkl.pkl"

for process in processes:
    if "*" in processes[process]: 
        processes[process] = []
        for subprocess in Xsec_json[process]:
            processes[process].append(subprocess) 

hists = {}
sumW = {}
for year in years:
    hists[year] = {}
    sumW[year] = {}
    for process in processes:
        hists[year][process] = {}
        sumW[year][process] = {}
        for subprocess in processes[process]:
            hists[year][process][subprocess] = {}
            sumW[year][process][subprocess] = 0.
            for column in bins:
                hists[year][process][subprocess][column] = ROOT.TH1D(f"Y{year}__{process}__{subprocess}__{column}", f"Y{year}__{process}__{subprocess}__{column}", len(bins[column]) - 1, bins[column])


for f in files:
    year = None; process = None; subprocess = None
    year = next((_year for _year in years if _year + "__" in f ), None)
    process = next((_process for _process in processes if _process + "__" in f ), None)
    if process is not None: 
        subprocess = next((_subprocess for _subprocess in processes[process] if f"__{process}__{_subprocess}"  in f ), None)
    if not (year and process and subprocess): continue
    print("loading: ", f)
    W = ROOT.RDataFrame("Runs", f).Sum("genEventSumw").GetValue()
    sumW[year][process][subprocess] += W
    Events = ROOT.RDataFrame("Events", f)
    if Events.Count().GetValue() < 1: continue
    for column in bins:
        h_column = Events.Histo1D((f"{f.replace(':', '_').replace('/', '_').replace('.', '_')}_{column}", f"{f.replace(':', '_').replace('/', '_').replace('.', '_')}_{column}", len(bins[column]) - 1, bins[column] ), column, "weight_All__nominal" ).GetValue()
        hists[year][process][subprocess][column].Add(h_column)

for year in years:
    for process in processes:
        for subprocess in processes[process]:
            for column in bins:
                hists[year][process][subprocess][column].Scale(1/sumW[year][process][subprocess])

with open(output_pkl, "wb") as f:
    pkl.dump(hists, f)


