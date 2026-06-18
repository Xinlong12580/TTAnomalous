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
#-----------------------------------loading files for the templates --------------------------------------------
#with open(DIR_TOP + "/outputList/output_selection_1p1.txt") as f:
with open(DIR_TOP + "/outputList/output_quick_selection.txt") as f:
    lines = f.readlines()
    data_files =[ line.strip() for line in lines]
data_files = [data_file for data_file in data_files if ((not ("Templates" in data_file)) and "RegSig" in data_file and "nom" in data_file and "RegSig" in data_file)]
template_files = []
for data_file in data_files:
    data_files_part = data_file.partition("Reg")
    template_file = data_files_part[0] + "Templates_" + data_files_part[1] + data_files_part[2]
    template_files.append(template_file)
    
with open(DIR_TOP + "/raw_nano/Luminosity.json") as f:
    lumi_json = json.load(f)

with open(DIR_TOP + "/raw_nano/Xsections_background.json") as f:
    Xsec_json = json.load(f)

#with open(DIR_TOP + "/raw_nano/Datasets_signal_v15.json") as f:
#    signal_json=json.load(f)
#----------------------------- set bins, variable columns and other configs---------------------------------------------------------------------
years = ["2022", "2022EE", "2023", "2023BPix", "2024"]
years = ["2024"]
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

#bins["leadingFatJetMsoftdrop"] = array.array("d", np.linspace(0, 3000, 301) )
bins["reco_mX"] = array.array("d", np.linspace(0, 5000, 501) )
bins["reco_mH"] = array.array("d", np.linspace(0, 3000, 301) )
bins["reco_mY"] = array.array("d", np.linspace(0, 3000, 301) )
for column in bins:
    bin_centers[column] = 0.5 * (np.array(bins[column])[:-1] + np.array(bins[column])[1:])
MC_weight = "weight_All__nominal"

processes = { "MC_TTBarJets": ["*"]}
save_name = "pkls/hists_selection_TH.pkl" 
root_save_name = "All_selection.root" 


load_TH1(data_files, template_files, years, bins, processes, MC_weight, save_name, root_save_name, Xsec_json, "")
