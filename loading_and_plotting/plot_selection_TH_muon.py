import numpy as np
import matplotlib.pyplot as plt
import mplhep
from hist import Hist
import ROOT
import array
import json
import pickle
import os
import sys
DIR_TOP = os.environ["ANA_TOP"]
sys.path.append(DIR_TOP)
from TTAnomalous_Helper import *
with open("pkls/hists_selection_TH_muon.pkl", "rb") as f:
    hists = pickle.load(f)
with open(DIR_TOP + "raw_nano/color_scheme.json", "r") as f:
    color_json = json.load(f)
with open(DIR_TOP + "raw_nano/Luminosity.json", "r") as f:
    lumi_json = json.load(f)

h_data = hists["data"]
h_BKGs = hists["BKGs"]
#----------------------------- set bins, variable columns and other configs---------------------------------------------------------------------

bins = {}
bin_centers = {}
bins["Mass_JT"] = array.array("d", np.linspace(0, 2000, 201))
bins["Mass_AFJ"] = array.array("d", np.linspace(0, 2000, 201))

bins["Phi_JT"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )
bins["Phi_JB"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )
bins["Phi_Lep"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )
bins["Phi_AFJ"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )

bins["Eta_JT"] = array.array("d", np.linspace(-3, 3, 21) )
bins["Eta_JB"] = array.array("d", np.linspace(-3, 3, 21) )
bins["Eta_Lep"] = array.array("d", np.linspace(-3, 3, 21) )
bins["Eta_AFJ"] = array.array("d", np.linspace(-3, 3, 21) )

bins["Pt_JT"] = array.array("d", np.linspace(0, 2000, 201) )
bins["Pt_JB"] = array.array("d", np.linspace(0, 2000, 201) )
bins["Pt_Lep"] = array.array("d", np.linspace(0, 2000, 201) )
bins["Pt_AFJ"] = array.array("d", np.linspace(0, 2000, 201) )

bins["Tagger_JB"] = array.array("d", np.linspace(0, 1, 101) )
bins["Tagger_JT"] = array.array("d", np.linspace(0, 1, 101) )
bins["Tagger_AFJ"] = array.array("d", np.linspace(0, 1, 101) )


for column in bins:
    bin_centers[column] = 0.5 * (np.array(bins[column])[:-1] + np.array(bins[column])[1:])
#MC_weight = "lumiXsecWeight"
MC_weight = "genWeight"
mplhep.style.use("CMS")
processes = { "MC_TTBarJets": ["*"], "MC_QCDJets": ["*"], "MC_WJets": ["*"], "MC_SingleTopJets": ["*"], "MC_DYJets": ["*"], "MC_TTHJets_Hto2B": ["*"], "MC_TTHJets_Hto2C": ["*"], "MC_TTHJets_Hto2G": ["*"], "MC_TTZJets_ZtoQQ":["*"], "MC_TTTT": ["*"], "MC_TTLL_MLL50":["*"], "MC_TTH_TTToAll_HToAATo4B_M30": ["*"]  }

Signal_processes = {"MC_TTHJets_Hto2B": ["*"], "MC_TTHJets_Hto2C": ["*"], "MC_TTHJets_Hto2G": ["*"], "MC_TTZJets_ZtoQQ":["*"], "MC_TTTT": ["*"], "MC_TTLL_MLL50":["*"], "MC_TTH_TTToAll_HToAATo4B_M30": ["*"]  }
years = [ "2024"]
save_dir = "plots/plots_selection_TH_muon"
#-------------------------------------rebinning -----------------------------------------
rebinned_h_data = {}
rebinned_h_BKGs = {}
for year in h_data:
    rebinned_h_data[year] = {}
    for column in h_data[year]:
        if column not in bins:
            continue
        rebinned_h_data[year][column] = rebin_TH1(h_data[year][column], bins[column])
        print(h_data[year][column].Integral())
for year in h_BKGs:
    rebinned_h_BKGs[year] = {}
    for process in h_BKGs[year]:
        rebinned_h_BKGs[year][process] = {}
        for subprocess in h_BKGs[year][process]:
            rebinned_h_BKGs[year][process][subprocess] = {}
            for column in h_BKGs[year][process][subprocess]:
                if column not in bins:
                    continue
                rebinned_h_BKGs[year][process][subprocess][column] = rebin_TH1(h_BKGs[year][process][subprocess][column], bins[column])
#--------------------- extracting interested processes-----------------------------------------------
data_binned = {}
data_binned_error = {}
for year in years:
    data_binned[year] = {}
    data_binned_error[year] = {}
    for column in bins:
        data_binned[year][column] = [rebinned_h_data[year][column].GetBinContent(i) for i in range(1, rebinned_h_data[year][column].GetNbinsX() + 1)]
        data_binned_error[year][column] = [rebinned_h_data[year][column].GetBinError(i) for i in range(1, rebinned_h_data[year][column].GetNbinsX() + 1)]
h_Merged = {}
h_All = {}
ratio = {}
ratio_error = {}
for year in years:
    h_Merged[year] = {}
    h_All[year] = {}
    ratio[year] = {}
    ratio_error[year] = {}
    for process in rebinned_h_BKGs[year]:
        h_Merged[year][process] = {}
        for column in bins:
            h_Merged[year][process][column] = ROOT.TH1D(f"selection_{process}_{year}_{column}", f"{year}_{column}", len(bins[column]) - 1, bins[column])
            h_All[year][column] = ROOT.TH1D(f"selection_MC_All_{year}_{column}", f"{year}_{column}", len(bins[column]) - 1, bins[column])
            ratio[year][column] = []
            ratio_error[year][column] = []
for year in years:
    for process in rebinned_h_BKGs[year]:
        for subprocess in rebinned_h_BKGs[year][process]:
            for column in bins:
                h_Merged[year][process][column].Add(rebinned_h_BKGs[year][process][subprocess][column])

    for column in bins:
        for process in h_Merged[year]:
                if process in Signal_processes: continue
                h_All[year][column].Add(h_Merged[year][process][column])
        values = np.array([h_All[year][column].GetBinContent(i) for i in range(1, h_All[year][column].GetNbinsX() + 1)] )
        errors = np.array([h_All[year][column].GetBinError(i) for i in range(1, h_All[year][column].GetNbinsX() + 1)] )
        ratio[year][column] = [x / y for x,y in zip(data_binned[year][column], values)]
        ratio_error[year][column] = [ max(0, x / y) for x,y in zip(data_binned_error[year][column], values)]



#-------------------------------Ploting -----------------------------------------------------------

for year in years:
    for column in bins:

        colors = []
        labels = []
        hs = []
        for process in processes:
            if process in Signal_processes: continue
            print(year) 
            colors.append(color_json[process])
            labels.append(process)
            hs.append(h_Merged[year][process][column])
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

        ax1.errorbar(bin_centers[column], data_binned[year][column], yerr=data_binned_error[year][column], fmt='o', color='black', label='Data')
        mplhep.histplot(
            hs,
            label = labels,
            color = colors,
            stack = True,
            histtype = "fill",
            ax = ax1,
        )
        mplhep.histplot(
            hs ,
            stack = True,  # Note: keep stack=True so contours align with total stacks
            histtype = "step",
            color = "black",
            ax = ax1,
            linewidth = 1.2,
        )
        mplhep.cms.label("Preliminary", data = False, rlabel = f"{((lumi_json[year])/1000):.2f}"  + r"$fb^{-1}$, "+ year + "(13.6 TeV)", ax = ax1)
        ax1.set_ylabel("Event Counts")
        ax1.set_xlabel("")
        ax1.legend()
        ax2.errorbar(bin_centers[column], ratio[year][column], yerr=ratio_error[year][column], fmt='o', color='black', label='Data')
        ax2.axhline(y = 1, linestyle = '--', color = 'red', linewidth = 1.5)
        ax2.set_ylabel("Data/MC")
        ax2.set_ylim(0, 2)
        ax2.set_xlabel(column)

        fig.tight_layout()
        ax1.set_yscale("linear")
        ax1.set_ylim(auto = True)
        fig.savefig(f"{save_dir}/linear_stack_{year}_{column}.png")
        ax1.set_yscale("log")
        ax1.set_ylim(1,10000000)
        fig.savefig(f"{save_dir}/stack_{year}_{column}.png")
        plt.close()
    
        #----plotting signal------
        for Signal_process in Signal_processes:
            fig_s, (ax1_s, ax2_s) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
            mplhep.histplot(
                [h_Merged[year][Signal_process][column] ],
                label = [Signal_process],
                color = ["purple"],
                stack = True,
                histtype = "fill",
                ax = ax1_s,
            )
            mplhep.histplot(
                [h_Merged[year][Signal_process][column] ],
                stack = True,  # Note: keep stack=True so contours align with total stacks
                histtype = "step",
                color = "black",
                ax = ax1_s,
                linewidth = 1.2,
            )
        
            mplhep.cms.label("Preliminary", data = False, rlabel = f"{((lumi_json[year])/1000):.2f}" + r"$fb^{-1}$, "+ year + "(13.6 TeV)", ax = ax1_s)
            ax1_s.set_ylabel("Event Counts")
            ax1_s.set_xlabel("")
            ax1_s.legend()

            ax2_s.set_xlabel(column)

            fig_s.tight_layout()
            ax1_s.set_yscale("linear")
            ax1_s.set_ylim(auto = True)
            fig_s.savefig(f"{save_dir}/linear_signal_{Signal_process}_{year}_{column}.png")
            ax1_s.set_yscale("log")
            fig_s.savefig(f"{save_dir}/signal_{Signal_process}_{year}_{column}.png")
            plt.close()
        
