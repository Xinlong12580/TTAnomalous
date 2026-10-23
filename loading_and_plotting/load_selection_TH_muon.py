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
data_files = [data_file for data_file in data_files if ((not ("Templates" in data_file)) and "RegSig" in data_file and "RegSig" in data_file and "/Muon" in data_file )]
template_files = []
for data_file in data_files:
    data_files_part = data_file.partition("Muon_RegSig")
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

for column in bins:
    bin_centers[column] = 0.5 * (np.array(bins[column])[:-1] + np.array(bins[column])[1:])
MC_weight = "weight_All__nominal"

processes = { "MC_TTBarJets": ["*"], "MC_QCDJets": ["*"], "MC_WJets": ["*"], "MC_SingleTopJets": ["*"], "MC_DYJets": ["*"], "MC_TTHJets_Hto2B": ["*"], "MC_TTHJets_Hto2C": ["*"], "MC_TTHJets_Hto2G": ["*"], "MC_TTZJets_ZtoQQ":["*"], "MC_TTTT": ["*"], "MC_TTLL_MLL50":["*"], "MC_TTH_TTToAll_HToAATo4B_M30": ["*"] }
save_name = "pkls/hists_selection_TH_muon.pkl" 
root_save_name = "All_selection_muon.root" 


load_TH1(data_files, template_files, years, bins, processes, MC_weight, save_name, root_save_name, Xsec_json, "")
