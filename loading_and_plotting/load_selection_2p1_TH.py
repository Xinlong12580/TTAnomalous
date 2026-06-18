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
#-----------------------------------loading files for the templates --------------------------------------------
with open(DIR_TOP + "outputList/output_selection_2p1_BDT.txt") as f:
    lines = f.readlines()
    data_files =[ line.strip() for line in lines]
data_files = [data_file for data_file in data_files if ((not ("Templates" in data_file)) and "nom" in data_file and "RegSig" in data_file)]
template_files = []
for data_file in data_files:
    data_files_part = data_file.partition("Reg")
    template_file = data_files_part[0] + "Templates_" + data_files_part[1] + data_files_part[2]
    template_files.append(template_file)
    
with open(DIR_TOP + "raw_nano/Luminosity.json") as f:
    lumi_json = json.load(f)

with open(DIR_TOP + "raw_nano/Xsections_background.json") as f:
    Xsec_json = json.load(f)

with open(DIR_TOP + "raw_nano/Datasets_signal_v15.json") as f:
    signal_json=json.load(f)
#----------------------------- set bins, variable columns and other configs---------------------------------------------------------------------
years = ["2022", "2022EE", "2023", "2023BPix", "2024"]
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
bins["reco_mH"] = array.array("d", np.linspace(0, 1500, 51) )
bins["reco_mY"] = array.array("d", np.linspace(0, 1500, 51) )
bins["reco_mX"] = array.array("d", np.linspace(1000, 4000, 51) )


for column in bins:
    bin_centers[column] = 0.5 * (np.array(bins[column])[:-1] + np.array(bins[column])[1:])
MC_weight = "weight_All__nominal"

processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"], "MC_DibosonJets": ["*"], "MC_SingleTopJets": ["*"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}
save_name = "pkls/hists_selection_2p1_TH.pkl" 
root_save_name = "All_selection_2p1.root" 

load_TH1(data_files, template_files, years, bins, processes, MC_weight, save_name, root_save_name, Xsec_json, signal_json)
