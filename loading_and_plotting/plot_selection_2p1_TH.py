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
from XHY4b_Helper import *
with open("pkls/hists_selection_2p1_TH.pkl", "rb") as f:
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
bins["PtJY0"] = array.array("d", np.linspace(0, 3000, 101))
bins["PtJY1"] =array.array("d", np.linspace(0, 3000, 101) )
bins["PtHiggsCandidate"] =array.array("d", np.linspace(0, 3000, 101) )

bins["PhiJY0"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )
bins["PhiJY1"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )
bins["PhiHiggsCandidate"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )

bins["EtaJY0"] = array.array("d", np.linspace(-3, 3, 21) )
bins["EtaJY1"] = array.array("d", np.linspace(-3, 3, 21) )
bins["EtaHiggsCandidate"] = array.array("d", np.linspace(-3, 3, 21) )

bins["MassJY0"] = array.array("d", np.linspace(0, 1500, 51) )
bins["MassJY1"] = array.array("d", np.linspace(0, 5000, 101) )
bins["reco_mY"] = array.array("d", np.linspace(0, 1500, 51) )
bins["reco_mH"] = array.array("d", np.linspace(0, 1500, 51) )
bins["reco_mX"] = array.array("d", np.linspace(1000, 4000, 51) )
for column in bins:
    bin_centers[column] = 0.5 * (np.array(bins[column])[:-1] + np.array(bins[column])[1:])
#MC_weight = "lumiXsecWeight"
MC_weight = "genWeight"
mplhep.style.use("CMS")
years = ["2022", "2022EE", "2023", "2023BPix", "2024"]
processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"], "MC_DibosonJets": ["*"], "MC_SingleTopJets": ["*"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}
processes = [ "MC_TTBarJets", "MC_QCDJets"]
save_dir = "plots/plots_selection_2p1_TH"
#-------------------------------------rebinning -----------------------------------------
rebinned_h_data = {}
rebinned_h_BKGs = {}
for year in h_data:
    rebinned_h_data[year] = {}
    for column in h_data[year]:
        if column not in bins:
            continue
        rebinned_h_data[year][column] = rebin_TH1(h_data[year][column], bins[column])

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

h_QCD = {}
h_WZ = {}
h_Higgs = {}
h_TTBar = {}
h_Diboson = {}
h_SingleTop = {}
h_Signal = {}
h_All = {}
ratio = {}
ratio_error = {}
for year in years:
    h_QCD[year] = {}
    h_WZ[year] = {}
    h_Higgs[year] = {}
    h_TTBar[year] = {}
    h_Diboson[year] = {}
    h_SingleTop[year] = {}
    h_Signal[year] = {}
    h_All[year] = {}
    ratio[year] = {}
    ratio_error[year] = {}

    for column in bins:
        h_QCD[year][column] = ROOT.TH1D(f"selection_MC_QCD_{year}_{column}", f"{year}_{column}", len(bins[column]) - 1, bins[column])
        h_WZ[year][column] = ROOT.TH1D(f"selection_MC_WZ_{year}_{column}", f"{year}_{column}", len(bins[column]) - 1, bins[column])
        h_Higgs[year][column] = ROOT.TH1D(f"selection_MC_Higgs_{year}_{column}", f"{year}_{column}", len(bins[column]) - 1, bins[column])
        h_TTBar[year][column] = ROOT.TH1D(f"selection_MC_TTBar_{year}_{column}", f"{year}_{column}", len(bins[column]) - 1, bins[column])
        h_Diboson[year][column] = ROOT.TH1D(f"selection_MC_Diboson_{year}_{column}", f"{year}_{column}", len(bins[column]) - 1, bins[column])
        h_SingleTop[year][column] = ROOT.TH1D(f"selection_MC_SingleTop_{year}_{column}", f"{year}_{column}", len(bins[column]) - 1, bins[column])
        h_Signal[year][column] = ROOT.TH1D(f"selection_MC_Signal_{year}_{column}", f"{year}_{column}", len(bins[column]) - 1, bins[column])
        h_All[year][column] = ROOT.TH1D(f"selection_MC_All_{year}_{column}", f"{year}_{column}", len(bins[column]) - 1, bins[column])
        ratio[year][column] = []
        ratio_error[year][column] = []
for year in years:
    for subprocess in h_BKGs[year]["MC_QCDJets"]:
        if subprocess == "QCD-4Jets_HT-100to200" or subprocess == "QCD-4Jets_HT-200to400": #This one seems to be buggy, ignore it
            continue
        for column in bins:
            h_QCD[year][column].Add(rebinned_h_BKGs[year]["MC_QCDJets"][subprocess][column])

    for subprocess in h_BKGs[year]["MC_WZJets"]:
        for column in bins:
            h_WZ[year][column].Add(rebinned_h_BKGs[year]["MC_WZJets"][subprocess][column])

    for subprocess in h_BKGs[year]["MC_HiggsJets"]:
        #if subprocess == "WplusH_Hto2B_Wto2Q_M-125": #This one seems to be buggy, ignore it
        #    continue
        for column in bins:
            h_Higgs[year][column].Add(rebinned_h_BKGs[year]["MC_HiggsJets"][subprocess][column])

    for subprocess in h_BKGs[year]["MC_TTBarJets"]:
        for column in bins:
            h_TTBar[year][column].Add(rebinned_h_BKGs[year]["MC_TTBarJets"][subprocess][column])

    for subprocess in h_BKGs[year]["MC_DibosonJets"]:
        for column in bins:
            h_Diboson[year][column].Add(rebinned_h_BKGs[year]["MC_DibosonJets"][subprocess][column])

    for subprocess in h_BKGs[year]["MC_SingleTopJets"]:
        for column in bins:
            h_SingleTop[year][column].Add(rebinned_h_BKGs[year]["MC_SingleTopJets"][subprocess][column])

    for subprocess in h_BKGs[year]["SignalMC_XHY4b"]:
        for column in bins:
            h_Signal[year][column].Add(rebinned_h_BKGs[year]["SignalMC_XHY4b"][subprocess][column])

    for column in bins:
        for hist in [h_QCD[year][column], h_WZ[year][column], h_TTBar[year][column], h_Higgs[year][column], h_Diboson[year][column], h_SingleTop[year][column]]:
            h_All[year][column].Add(hist)
        values = np.array([h_All[year][column].GetBinContent(i) for i in range(1, h_All[year][column].GetNbinsX() + 1)] )
        errors = np.array([h_All[year][column].GetBinError(i) for i in range(1, h_All[year][column].GetNbinsX() + 1)] )
        ratio[year][column] = [x / y for x,y in zip(data_binned[year][column], values)]
        ratio_error[year][column] = [x / y for x,y in zip(data_binned_error[year][column], values)]



#-------------------------------Ploting -----------------------------------------------------------

colors = [color_json["MC_SingleTopJets"], color_json["MC_DibosonJets"], color_json["MC_HiggsJets"], color_json["MC_TTBarJets"], color_json["MC_WZJets"], color_json["MC_QCDJets"]]
h_dict = {"MC_SingleTopJets":h_SingleTop, "MC_DibosonJets":h_Diboson, "MC_HiggsJets":h_Higgs, "MC_TTBarJets":h_TTBar, "MC_WZJets":h_WZ, "MC_QCDJets":h_QCD}
for year in years:
    for column in bins:
        labels = []
        colors = []
        hs = []
        for process in processes:
            print(year) 
            colors.append(color_json[process])
            labels.append(process)
            hs.append(h_dict[process][year][column])

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
            [h_SingleTop[year][column], h_Diboson[year][column], h_Higgs[year][column], h_TTBar[year][column], h_WZ[year][column], h_QCD[year][column] ],
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

    
        #----plotting signal------

        fig_s, (ax1_s, ax2_s) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)
        mplhep.histplot(
            [h_Signal[year][column] ],
            label = ["Signal MX-3000_MY-300 (1 pb)"],
            color = ["purple"],
            stack = True,
            histtype = "fill",
            ax = ax1_s,
        )
        mplhep.histplot(
            [h_Signal[year][column] ],
            stack = True,  # Note: keep stack=True so contours align with total stacks
            histtype = "step",
            color = "black",
            ax = ax1_s,
            linewidth = 1.2,
        )
    
        mplhep.cms.label("Preliminary", data = False, rlabel = f"{((lumi_json[year])/1000):.2f}"  + r"$fb^{-1}$, "+ year + "(13.6 TeV)", ax = ax1_s)
        ax1_s.set_ylabel("Event Counts")
        ax1_s.set_xlabel("")
        ax1_s.legend()

        ax2_s.set_xlabel(column)

        fig_s.tight_layout()
        ax1_s.set_yscale("linear")
        ax1_s.set_ylim(auto = True)
        fig_s.savefig(f"{save_dir}/linear_signal_{year}_{column}.png")
        ax1_s.set_yscale("log")
        ax1_s.set_ylim(1,10000000)
        fig_s.savefig(f"{save_dir}/signal_{year}_{column}.png")
    
