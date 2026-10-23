import ROOT
import os
import sys
import array
import json
import math
import pickle as pkl
import matplotlib.pyplot as plt
DIR_TOP = os.environ["ANA_TOP"]
sys.path.append(DIR_TOP)
from TTAnomalous_Helper import *
with open(DIR_TOP + "/raw_nano/Xsections_background.json") as f:
    Xsec_json = json.load(f)

with open("hists_selection_TH_muon.pkl", "rb") as f:
    hists = pkl.load(f)["BKGs"]
save_dir = "plots/"
samples = np.arange(0, 1, 100)
processes = {"MC_TTBarJets":"*", "MC_TTHJets": "*"}
years = ["2024"]
bins = {"Tagger_AFJ": array.array("d", np.linspace(0, 1, 101) )}
for process in processes:
    if "*" in processes[process]: 
        processes[process] = []
        for subprocess in Xsec_json[process]:
            processes[process].append(subprocess) 

NPass = {}
for year in years:
    NPass[year] = {}
    for process in processes:
        NPass[year][process] = {}
        for subprocess in processes[process]:
            NPass[year][process][subprocess] = {}
            for column in bins:
                NPass[year][process][subprocess][column] = {}
                for threshold in bins[column]:
                    bin_start = hists[year][process][subprocess][column].GetXaxis().FindBin(threshold)
                    NPass[year][process][subprocess][column][threshold] = hists[year][process][subprocess][column].Integral(bin_start, hists[year][process][subprocess][column].GetNbinsX())
                NPass[year][process][subprocess][column]["all"] = hists[year][process][subprocess][column].Integral()
    
       

BKGs = {"MC_TTBarJets":"*"} 
Signals = {"MC_TTHJets":"*"} 
    
for process in BKGs:
    if "*" in BKGs[process]: 
        BKGs[process] = []
        for subprocess in Xsec_json[process]:
            BKGs[process].append(subprocess) 

for process in Signals:
    if "*" in Signals[process]: 
        Signals[process] = []
        for subprocess in Xsec_json[process]:
            Signals[process].append(subprocess) 

for year in years:
    NPass[year]["BKGs"] = {}
    for column in bins:
        NPass[year]["BKGs"][column] = {}
        for threshold in bins[column]:
            NPass[year]["BKGs"][column][threshold] = 0.
        NPass[year]["BKGs"][column]["all"] = 0.
        for process in BKGs:
            for subprocess in BKGs[process]:
                NPass[year]["BKGs"][column]["all"] += NPass[year][process][subprocess][column]["all"]
                for threshold in bins[column]:
                    NPass[year]["BKGs"][column][threshold] += NPass[year][process][subprocess][column][threshold]

Acceptance = {}
        
for year in years:
    Acceptance[year] = {}
    Acceptance[year]["BKGs"] = {}
    for column in bins:
        Acceptance[year]["BKGs"][column] = {}
        for threshold in bins[column]:
            Acceptance[year]["BKGs"][column][threshold] = NPass[year]["BKGs"][column][threshold] / max(1e-6, NPass[year]["BKGs"][column]["all"])
    for process in Signals:
        Acceptance[year][process] = {}
        for subprocess in Signals[process]:
            Acceptance[year][process][subprocess] = {}
            for column in bins:
                Acceptance[year][process][subprocess][column] = {}
                for threshold in bins[column]:
                    Acceptance[year][process][subprocess][column][threshold] = NPass[year][process][subprocess][column][threshold] / max(1e-6, NPass[year][process][subprocess][column]["all"])
                                     

for year in years:
    for process in Signals:
        for subprocess in Signals[process]:
            signal_Acceptance = {}
            bkg_Acceptance = {}
            SoverSqrtB = {}
            NPassB = {}
            NPassS = {}
            for column in bins:
                signal_Acceptance[column] = [] 
                bkg_Acceptance[column] =  []
                SoverSqrtB[column] =  []
                NPassB[column] =  []
                NPassS[column] =  []
                for threshold in bins[column]:
                    signal_Acceptance[column].append(Acceptance[year][process][subprocess][column][threshold])
                    bkg_Acceptance[column].append(Acceptance[year]["BKGs"][column][threshold])
                    SoverSqrtB[column].append(NPass[year][process][subprocess][column][threshold] / math.sqrt(max(1e-6, NPass[year]["BKGs"][column][threshold])) )
                    NPassB[column].append(NPass[year]["BKGs"][column][threshold])
                    NPassS[column].append(NPass[year][process][subprocess][column][threshold])
            fig = plt.figure()
            ax = fig.add_subplot(111)
            for column in bins:
                AUC = 0.
                for i in range(len(bkg_Acceptance[column]) - 1):
                    AUC += (bkg_Acceptance[column][i] - bkg_Acceptance[column][i+1]) * (signal_Acceptance[column][i + 1] + signal_Acceptance[column][i]) / 2
                ax.plot(bkg_Acceptance[column], signal_Acceptance[column], label = f"{column}, AUC = {AUC:.3f}")
            ax.legend()
            ax.set_xlabel("Background Acceptance")
            ax.set_ylabel("Signal Acceptance")
            ax.set_title(f"Signal({process} {subprocess}) vs BKG ROC, {year}")
            fig.savefig(f"{save_dir}/{year}_{process}_{subprocess}_ROC.png")

            fig = plt.figure()
            ax = fig.add_subplot(111)
            for column in bins:
                max_value = max(SoverSqrtB[column])
                max_index = SoverSqrtB[column].index(max_value)
                max_score = bins[column][max_index]
                ax.plot(bins[column], SoverSqrtB[column], label = f"{column}, max value = {max_value:.3f} at score = {max_score}")
            ax.legend()
            ax.set_xlabel("Score")
            ax.set_ylabel(r"$\frac{S}{\sqrt{B}}$")
            ax.set_title(f"Signal({process} {subprocess}) vs BKG, S/Sqrt(B), {year}")
            fig.savefig(f"{save_dir}/{year}_{process}_{subprocess}_SoverSqrtB.png")
            
            fig = plt.figure()
            ax = fig.add_subplot(111)
            for column in bins:
                ax.plot(bins[column], NPassB[column], label = f"{column}")
            ax.legend()
            ax.set_xlabel("Score")
            ax.set_ylabel("Count")
            ax.set_title(f"Signal({process} {subprocess}) vs BKG, BKG NPass, {year}")
            fig.savefig(f"{save_dir}/{year}_{process}_{subprocess}_NPassB.png")

            
            fig = plt.figure()
            ax = fig.add_subplot(111)
            for column in bins:
                ax.plot(bins[column], NPassS[column], label = f"{column}")
            ax.legend()
            ax.set_xlabel("Score")
            ax.set_ylabel("Count")
            ax.set_title(f"Signal({process} {subprocess}) vs BKG, Signal NPass, {year}")
            fig.savefig(f"{save_dir}/{year}_{process}_{subprocess}_NPassS.png")

            
