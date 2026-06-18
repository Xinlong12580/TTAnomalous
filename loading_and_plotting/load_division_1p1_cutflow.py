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
print("TEST")
#-----------------------------------loading files for the templates --------------------------------------------
with open(DIR_TOP + "outputList/output_division_1p1_BDT.txt") as f:
#with open(DIR_TOP + "outputList/output_selection_1p1_debug.txt") as f:
    lines = f.readlines()
    data_files =[line.strip() for line in lines if "RegSig" in line and   "nom" in line and "Templates" not in line and "output.log" not in line]
    #data_files =[line.strip() for line in lines if "nom" in line and "Templates" not in line and "output.log" not in line]

with open(DIR_TOP + "raw_nano/Luminosity.json") as f:
    lumi_json = json.load(f)

with open(DIR_TOP + "raw_nano/Xsections_background.json") as f:
    Xsec_json = json.load(f)

with open(DIR_TOP + "raw_nano/Datasets_signal_v15.json") as f:
    signal_json=json.load(f)

#----------------------------- set bins, variable columns and other configs--------------------------------------------------------------------
  
cuts = ["Region_SR1", "BeforeSkim", "Skim", "GoldenJson", "SkimOf1p1", "LeptonVeto", "TriggerCut", "FlagCut", "FatJetID", "FatJetPt", "FatJetMass", "DeltaEta", "MassJJ", "HiggsMatch"]
cuts = [ "BeforeSkim", "Skim", "GoldenJson", "SkimOf1p1", "JERCJetVeto", "LeptonVeto", "TriggerCut", "FlagCut", "FatJetID", "FatJetPt", "FatJetMass", "DeltaEta", "MassJJ", "HiggsMatch", "Region_SR2"]
cuts = [ "BeforeSkim", "SkimOf1p1Or2p1", "GoldenJson", "SkimOf1p1", "NoiseFilter", "LeptonVeto", "JERCJetVeto", "TriggerCut", "HiggsMatch", "MXCut", "MYCut", "minTagger_H", "minTagger_Y" ]
cutflows = {}
years = ["2022", "2022EE", "2023", "2023BPix", "2024"]
for cut in cuts:
    cutflows[cut] = {}
    for year in years:
        cutflows[cut][year] = {}
MC_weight = "genWeight"
mplhep.style.use("CMS")

processes = {"MC_QCDJets": ["*"], "MC_WZJets": ["*"], "MC_HiggsJets": ["*"], "MC_TTBarJets": ["*"], "MC_DibosonJets": ["*"], "MC_SingleTopJets": ["*"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}
processes = {"MC_QCDJets": ["*"], "MC_TTBarJets": ["*"], "SignalMC_XHY4b": ["MX-3000_MY-300"]}
save_name = "pkls/hists_division_1p1_cutflow.pkl"
#------------------------------ making data template ------------------------------------------------------------
'''
print("Loading data")
for cut in cuts:
    for year in years:
        cutflows[cut][year]["data"] = {}
        cutflows[cut][year]["data"]["JetMET"] = 0

for data_file in data_files:
    if "JetMET" in data_file:
        for year in years:
            if (year + "__") in data_file:
                print(data_file)
                rdf = ROOT.RDataFrame("Cutflow", data_file)
                if rdf.Count().GetValue() < 1:
                    print("Empty File")
                else:
                    rdf_np = rdf.AsNumpy()
                    for cut in cuts:
                         cutflows[cut][year]["data"]["JetMET"] += sum(rdf_np[cut])

print("Loading data successful")
'''
#-----------------making BKG templates -----------------------------------------------------------------

#defining and initiating weight info for scaling

BKG_fileWeight, BKG_totalWeight = load_weight(data_files, years, processes, signal_json, Xsec_json)
for cut in cuts:            
    for year in years:
        for process in processes:
            cutflows[cut][year][process] = {}
            for subprocess in processes[process]:
                if subprocess == "*":
                    if "SignalMC_" in process:
                        for _subprocess in signal_json[year][process]:
                            cutflows[cut][year][process][_subprocess] = 0
                        break
                    elif "MC_" in process:
                        for _subprocess in Xsec_json[process]:
                            cutflows[cut][year][process][_subprocess] = 0
                        break
                else:
                    cutflows[cut][year][process][subprocess] = 0


print("Loading BKG")


# making templates
for data_file in data_files:
    for year in cutflows["BeforeSkim"]:
        lumi = lumi_json[year]
        if (year + "__" ) in data_file:
            for process in cutflows["BeforeSkim"][year]:
                if process in data_file:
                    for subprocess in cutflows["BeforeSkim"][year][process]:
                        if subprocess in data_file:
                            print(data_file)
                            if "SignalMC_" in process:
                                Xsec = 1
                            elif "MC_" in process:
                                Xsec = Xsec_json[process][subprocess]
                            rdf = ROOT.RDataFrame("Cutflow", data_file )
                            if rdf.Count().GetValue() <= 0 or len(rdf.GetColumnNames()) < 1:
                                print("Empty File")
                            else:
                                rdf_np = rdf.AsNumpy()
                                for cut in cuts:
                                    print(sum(rdf_np[cut]))
                                    cutflows[cut][year][process][subprocess] += sum(rdf_np[cut]) * (lumi * Xsec / BKG_totalWeight[year][process][subprocess])
        

with open(save_name, "wb") as f:
    pickle.dump(cutflows, f)

print("LOADING BKG SUCCESSFUL")
exit()

