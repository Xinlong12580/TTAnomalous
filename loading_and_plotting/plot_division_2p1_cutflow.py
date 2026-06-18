import pickle
import numpy as np
import matplotlib.pyplot as plt
import json
import os
import sys
DIR_TOP = os.environ["ANA_TOP"]
sys.path.append(DIR_TOP)
with open(DIR_TOP + "raw_nano/color_scheme.json", "r") as f:
    color_scheme = json.load(f)
#--------------------------------defining parameters---------------------------------------------------------
#cuts = [ "BeforeSkim", "Skim", "GoldenJson", "SkimOf1p1", "LeptonVeto", "TriggerCut", "FlagCut", "FatJetID", "FatJetPt", "FatJetMass", "DeltaEta", "MassJJ", "HiggsMatch", "Region_SR1"]
cuts = [ "BeforeSkim", "SkimOf1p1Or2p1", "GoldenJson", "SkimOf2p1", "NoiseFilter", "LeptonVeto", "JERCJetVeto", "TriggerCut", "HiggsMatch", "JYMatch", "MXCut", "MYCut", "minTagger_H", "minTagger_Y" ]
cutflows = {}
years = ["2022", "2022EE", "2023", "2023BPix", "2024"]
for cut in cuts:
    cutflows[cut] = {}
    for year in years:
        cutflows[cut][year] = {}
MC_weight = "genWeight"

with open("pkls/hists_division_2p1_cutflow.pkl", "rb") as f:
    cutflows = pickle.load(f)
save_dir = "plots/plots_division_2p1_cutflow"
#------------------------------ making plots ------------------------------------------------------------
#plotting individually
for year in years:
    fig = plt.figure(figsize = (20,12))
    ax = fig.add_subplot(1, 1, 1)
    x = np.arange(len(cuts))
    width = 0.3
    for process in cutflows["BeforeSkim"][year]:
        if process == "data":
            continue
        bars = np.zeros(len(cuts))
        for i in range(len(cuts)):
            cut = cuts[i]
            n = 0
            for subprocess in cutflows[cut][year][process]:
                n += cutflows[cut][year][process][subprocess]
            bars[i] = n
        print(year, process, bars)
        ax.bar(x - width/2, bars, width, edgecolor = color_scheme[process], linewidth = 3, facecolor = "none", label = (process if "Signal" not in process else "Signal MX-3000 MY-300")   ) 
        
    ax.set_ylabel("Events")
    ax.set_title(f"{year} Cutflow")
    ax.set_xticks(x)
    ax.set_xticklabels(cuts, rotation=45, ha='right')
    ax.set_yscale("log")
    ax.legend()
    fig.savefig(f"{save_dir}/{year}_cutflow.png")

#plotting S/sqrt(B)
for year in years:
    fig = plt.figure(figsize = (20,12))
    ax = fig.add_subplot(1, 1, 1)
    x = np.arange(len(cuts))
    width = 0.3
    counts_S = np.zeros(len(cuts))
    counts_B = np.zeros(len(cuts))
    for i in range(len(cuts)):
        n_B = 0
        n_S = 0
        cut = cuts[i]
        for process in cutflows[cut][year]:
            if process == "data":
                continue
            for subprocess in cutflows[cut][year][process]:
                if "Signal" in process:
                    n_S += cutflows[cut][year][process][subprocess]
                else:
                    n_B += cutflows[cut][year][process][subprocess]
        counts_B[i] = n_B
        counts_S[i] = n_S
    for S,B in zip(counts_S, counts_B):
        print(S, B) 
    print(type(n_B))
    bars = [S / np.sqrt(B) for S,B in zip(counts_S, counts_B)]   
    ax.bar(x - width/2, bars, width, label = process  ) 
        
    ax.set_ylabel("S/sqrt(B)")
    ax.set_title(f"{year} Cutflow")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(cuts, rotation=45, ha='right')
    ax.legend()
    fig.savefig(f"{save_dir}/{year}_SoverSqrtB.png")

#plotting S/sqrt(B)






