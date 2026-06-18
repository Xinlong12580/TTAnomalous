import numpy as np
import matplotlib.pyplot as plt
import mplhep
import ROOT
import array
import json
import pickle
import os
import sys
DIR_TOP = os.environ["ANA_TOP"]
sys.path.append(DIR_TOP)
from XHY4b_Helper import *
#-----------------------------------loading files for the templates --------------------------------------------
with open(DIR_TOP + "outputList/output_division_2p1.txt") as f:
    lines = f.readlines()
    all_data_files =[line.strip() for line in lines if "nom" in line and "Templates" not in line and "output.log" not in line]
all_template_files = []
for data_file in all_data_files:
    data_files_part = data_file.partition("2p1/")
    template_file = data_files_part[0] + data_files_part[1] + "Templates_" + data_files_part[2]
    all_template_files.append(template_file)
    
with open(DIR_TOP + "raw_nano/Luminosity.json") as f:
    lumi_json = json.load(f)

with open(DIR_TOP + "raw_nano/Xsections_background.json") as f:
    Xsec_json = json.load(f)

with open(DIR_TOP + "raw_nano/Datasets_signal.json") as f:
    signal_json=json.load(f)
#----------------------------- set bins, variable columns and other configs---------------------------------------------------------------------
years = ["2022", "2022EE", "2023", "2023BPix"]
processes = { "MC_QCDJets": ["QCD-4Jets_HT-400to600", "QCD-4Jets_HT-600to800", "QCD-4Jets_HT-800to1000", "QCD-4Jets_HT-1000to1200", "QCD-4Jets_HT-1200to1500", "QCD-4Jets_HT-1500to2000", "QCD-4Jets_HT-2000"], "MC_TTBarJets": ["TTto4Q", "TTtoLNu2Q", "TTto2L2Nu"], "MC_WZJets":["*"], "SignalMC_XHY4b": ["MX-3000_MY-95", "MX-3000_MY-200", "MX-3000_MY-300", "MX-3000_MY-1000"]}
for process in processes:
    if processes[process] == ["*"]:
        processes[process] = []
        if "SignalMC" in process:
            for mass in signal_json["2022"]["SignalMC_XHY4b"]:
                processes[process].append(mass)
        elif "MC" in process:
            for subprocess in Xsec_json[process]:
                processes[process].append(subprocess) 
regions = ["SR1", "SR2", "SB1", "SB2", "VS1", "VS2", "VS3", "VS4", "VB1", "VB2"]
bins={"MJJvsMJY":{"x":array.array("d", np.linspace(0, 5000, 501)), "y": array.array("d", np.linspace(0, 5000, 501))}}
 

MC_weight = "weight_All__nominal"
mplhep.style.use("CMS")

save_name = "pkls/hists_division_2p1_TH.pkl"
root_save_name = "All_division_2p1.root"
#------------------------------ making data template ------------------------------------------------------------
h_data = {}
h_BKGs = {}
for region in regions:
    data_files = [f for f in all_data_files if region in f]
    template_files = [f for f in all_template_files if region in f]
 
    _h_data, _h_BKGs = load_TH2(data_files, template_files, years, bins, processes, MC_weight, Xsec_json, signal_json, hist_name = ("division_" + region))
    h_data[region] = _h_data
    h_BKGs[region] = _h_BKGs
h_All = {"data" : h_data, "BKGs" : h_BKGs}
with open(save_name, "wb") as f:
    pickle.dump(h_All, f)
    
f = ROOT.TFile.Open(root_save_name, "RECREATE")
f.cd()
for region in h_data:
    for year in h_data[region]:
        for column in h_data[region][year]:
            h_data[region][year][column].Write()
    
for region in h_BKGs:
    for year in h_BKGs[region]:
        for process in h_BKGs[region][year]:
            for subprocess in h_BKGs[region][year][process]:
                for column in h_BKGs[region][year][process][subprocess]:
                    h_BKGs[region][year][process][subprocess][column].Write()
f.Close()
    
