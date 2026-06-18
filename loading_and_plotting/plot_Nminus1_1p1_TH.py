import numpy as np
import matplotlib.pyplot as plt
import mplhep
from hist import Hist
import ROOT
import array
import json
import pickle
import math
import os
import sys
DIR_TOP = os.environ["ANA_TOP"]
sys.path.append(DIR_TOP)
from XHY4b_Helper import *
with open("pkls/hists_Nminus1_1p1_TH.pkl", "rb") as f:
    hists = pickle.load(f)
with open(DIR_TOP + "raw_nano/color_scheme.json", "r") as f:
    color_scheme = json.load(f)
h_data = hists["data"]
h_BKGs = hists["BKGs"]
#----------------------------- set bins, variable columns and other configs---------------------------------------------------------------------

bins = {}

bins["PtHCut__FatJet_pt_0"] = array.array("d", np.linspace(0, 1000, 101))
bins["PtYCut__FatJet_pt_1"] = array.array("d", np.linspace(0, 1000, 101))
bins["DeltaEtaCut__deltaEta"] = array.array("d", np.linspace(0, 5, 101))
bins["BTaggingHCut__PNet_H"] = array.array("d", np.linspace(0, 1, 101))
bins["BTaggingYCut__PNet_Y"] = array.array("d", np.linspace(0, 1, 101))
cuts = {}
cuts["PtHCut__FatJet_pt_0"] = [450]
cuts["PtYCut__FatJet_pt_1"] = [450]
cuts["DeltaEtaCut__deltaEta"] = [1.6]
cuts["BTaggingHCut__PNet_H"] = [0.95]
cuts["BTaggingYCut__PNet_Y"] = [0.95]
processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"], "MC_DibosonJets": ["*"], "MC_SingleTopJets": ["*"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}
years = ["2022", "2022EE", "2023", "2023BPix"]
processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"], "MC_DibosonJets": ["*"], "MC_SingleTopJets": ["*"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}
save_dir = "plots/plots_Nminus1_1p1_TH"
#-------------------------------------rebinning -----------------------------------------
h_BKGs_rebinned = {}

for year in h_BKGs:
    h_BKGs_rebinned[year] = {}
    for process in h_BKGs[year]:
        h_BKGs_rebinned[year][process] = {}
        for subprocess in h_BKGs[year][process]:
            h_BKGs_rebinned[year][process][subprocess] = {}
            for column in h_BKGs[year][process][subprocess]:
                h_BKGs_rebinned[year][process][subprocess][column] = rebin_TH1(h_BKGs[year][process][subprocess][column], bins[column])
                if "Signal" in process:
                     h_BKGs_rebinned[year][process][subprocess][column].Scale(0.03)
h_BKGs_rebinned_merged = {}
for year in h_BKGs_rebinned:
    h_BKGs_rebinned_merged[year] = {}
    for process in h_BKGs_rebinned[year]:
        h_BKGs_rebinned_merged[year][process] = {}
        for column in  bins:
            h_BKGs_rebinned_merged[year][process][column] = h_BKGs_rebinned[year][process][next(iter(h_BKGs_rebinned[year][process]))][column].Clone("mergingSubprocess_MC_{year}_{process}_{column}")
            h_BKGs_rebinned_merged[year][process][column].Reset()
            print(process)
            for subprocess in h_BKGs_rebinned[year][process]:
                h_BKGs_rebinned_merged[year][process][column].Add(h_BKGs_rebinned[year][process][subprocess][column])
################################################################################################################################
#-----------------------------------------making 2D plots-------------------------
########################################################################################################################
#--------------------- extracting interested processes-----------------------------------------------



#-------------------------------Ploting -----------------------------------------------------------
directions = ["right", "left"]
for direction in directions:
    for year in years:
        for column in bins:

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
            hs = []
            labels = []
            colors = []
            h_BKG_rebinned_merged = h_BKGs_rebinned_merged[year]["MC_QCDJets"][column].Clone(f"{year}_{column}_ALL_BKG")
            h_BKG_rebinned_merged.Reset()
            h_Signal_rebinned_merged = h_BKGs_rebinned_merged[year]["MC_QCDJets"][column].Clone(f"{year}_{column}_ALL_Signal")
            h_Signal_rebinned_merged.Reset()
            for process in h_BKGs_rebinned_merged[year]:
                if "Signal" not in process:
                    h_BKG_rebinned_merged.Add(h_BKGs_rebinned_merged[year][process][column])
                else:
                    h_Signal_rebinned_merged.Add(h_BKGs_rebinned_merged[year][process][column])
                    
                labels.append(process)
                hs.append(h_BKGs_rebinned_merged[year][process][column])
                colors.append(color_scheme[process])
            if direction == "left":
                h_cum_BKG_rebinned_merged = h_BKG_rebinned_merged.GetCumulative(True, "cum_{direction}_{year}_{column}_ALL_BKG")
                h_cum_Signal_rebinned_merged =  h_Signal_rebinned_merged.GetCumulative(True, "cum_{direction}_{year}_{column}_ALL_Signal")
            if direction == "right":
                h_cum_BKG_rebinned_merged = h_BKG_rebinned_merged.GetCumulative(False, "cum_{direction}_{year}_{column}_ALL_BKG")
                h_cum_Signal_rebinned_merged =  h_Signal_rebinned_merged.GetCumulative(False, "cum_{direction}_{year}_{column}_ALL_Signal")
            Sigs = [h_cum_Signal_rebinned_merged.GetBinContent(i) / (1 + math.sqrt(max(0, h_cum_BKG_rebinned_merged.GetBinContent(i)))) for i in range(1, h_cum_BKG_rebinned_merged.GetNbinsX() + 1)] 
            Sigs.append(Sigs[-1]) 
            for i in range(1, h_BKG_rebinned_merged.GetNbinsX() + 1):
                if "BTagging" in column:
                    print(f"{direction} bin {i}")
                    print(h_BKG_rebinned_merged.GetBinContent(i))
                    print(h_Signal_rebinned_merged.GetBinContent(i))
                    print(h_cum_BKG_rebinned_merged.GetBinContent(i))
                    print(h_cum_Signal_rebinned_merged.GetBinContent(i))
                    print(Sigs[i])
            mplhep.histplot(
                hs,
                label = labels,
                color =  colors,
                stack = False,  # Note: keep stack=True so contours align with total stacks
                histtype = "step",
                yerr = False,
                ax = ax1,
                linewidth = 3,
            )
            mplhep.cms.label("Internal", data = False, rlabel = r"2022(13.6 TeV)", ax = ax1)
            ax1.set_ylabel("Event Counts")
            ax1.set_xlabel(column)
            ax1.legend(fontsize = "large")
            #ax2.step([(bins[column][i] + bins[column][i + 1]) / 2 for i in range(len(bins[column]) - 1)], Sigs, linewidth = 2, color='black')
            ax2.step(bins[column], Sigs, where = "post", linewidth = 2, color='black')
            #ax2.axhline(y = 1, linestyle = '--', color = 'red', linewidth = 1.5)
            ax2.set_ylabel("Significance")
            ax2.set_ylim(0, 2*max(Sigs))
            ax2.set_xlabel(column)
            for cut in cuts[column]:
                ax2.axvline(x = cut, color = "red", linewidth = 2)
            ax1.set_title(f"N-1 distribution, integral from {direction}")
            fig.tight_layout()
            ax1.set_yscale("linear")
            ax1.set_ylim(auto = True)
            fig.savefig(f"{save_dir}/linear_overlap_{direction}_{year}_{column}.png")
            ax1.set_yscale("log")
            ax1.set_ylim(auto = True)
            fig.savefig(f"{save_dir}/log_overlap_{direction}_{year}_{column}.png")

