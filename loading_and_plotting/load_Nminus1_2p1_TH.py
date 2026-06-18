import numpy as np
import matplotlib.pyplot as plt
import mplhep
from hist import Hist
import ROOT
import array
import json
import pickle
from XHY4b_Helper import *
import os
import sys
DIR_TOP = os.environ["ANA_TOP"]
sys.path.append(DIR_TOP)
print("TEST")
#-----------------------------------loading files for the templates --------------------------------------------
with open(DIR_TOP + "outputList/output_Nminus1_2p1.txt") as f:
    lines = f.readlines()
    data_files =[ line.strip() for line in lines]
data_files = [data_file for data_file in data_files if ((not ("Templates" in data_file)) and "nom" in data_file)]
template_files = []
for data_file in data_files:
    data_files_part = data_file.partition("nom")
    template_file = data_files_part[0] + "Templates_Nminus1_" + data_files_part[1] + data_files_part[2]
    template_files.append(template_file)
    
with open(DIR_TOP + "raw_nano/Luminosity.json") as f:
    lumi_json = json.load(f)

with open(DIR_TOP + "raw_nano/Xsections_background.json") as f:
    Xsec_json = json.load(f)

with open(DIR_TOP + "raw_nano/Datasets_signal.json") as f:
    signal_json=json.load(f)
#----------------------------- set bins, variable columns and other configs---------------------------------------------------------------------
years = ["2022", "2022EE", "2023", "2023BPix"]
bins = {}
bins["PtHCut__PtHiggsCandidate"] = array.array("d", np.linspace(0, 3000, 301))
bins["PtJY0Cut__PtJY0"] = array.array("d", np.linspace(0, 3000, 301))
bins["PtJY1Cut__PtJY1"] = array.array("d", np.linspace(0, 3000, 301))
bins["HiggsMassCut__MassHiggsCandidate"] = array.array("d", np.linspace(0, 3000, 301))
bins["DeltaRCut__DeltaR_JJ"] = array.array("d", np.linspace(0, 10, 101))
bins["MJJCut__MassJJH"] = array.array("d", np.linspace(0, 5000, 501))
bins["BTaggingHCut__PNet_H"] = array.array("d", np.linspace(0, 1, 101))
bins["BTaggingYCut__PNet_Y"] = array.array("d", np.linspace(0, 1, 101))
MC_weight = "weight_All__nominal"

processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"], "MC_DibosonJets": ["*"], "MC_SingleTopJets": ["*"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}
save_name = "pkls/hists_Nminus1_2p1_TH.pkl" 
root_save_name = "All_Nminus1_2p1.root" 


load_TH1(data_files, template_files, years, bins, processes, MC_weight, save_name, root_save_name, Xsec_json, signal_json)
