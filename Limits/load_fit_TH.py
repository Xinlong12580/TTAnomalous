import ROOT
import os
import numpy as np
import array
import json
from argparse import ArgumentParser
import os

parser=ArgumentParser()


parser.add_argument('--Reg', type=str, action='store', required=True)
parser.add_argument('--ngroup', type=int, action='store', default = 1, required=False)
parser.add_argument('--igroup', type=int, action='store', default = 1, required=False) #Requiring too much memory, so load in group instead
args = parser.parse_args()
with open("raw_nano/Luminosity.json") as f:
    lumi_json = json.load(f)

with open("raw_nano/Xsections_background.json") as f:
    Xsec_json = json.load(f)

#----------------------------- set bins, variable columns and other configs---------------------------------------------------------------------
if "Signal" in args.Reg:
    Reg = "SR"
if "Validation" in args.Reg:
    Reg = "VR"
if "Control" in args.Reg:
    Reg = "CR"
#with open(f"outputList/output_division_combined_BDT.txt") as f:
with open(f"outputList/output_division.txt") as f:
    lines = f.readlines()
    template_files =[ line.strip() for line in lines if "Templates" in line and "log" not in line and "Reg" + args.Reg[0:3] in line]

#all_systs = ["JMS_", "JMR_", "JER_", "PileUp_Corr", f"corr{hist_mode}_TriggerSF_MC", f"corr{hist_mode}_TriggerSF_data", "Pdfweight", "QCDScaleWeight", f"corr{hist_mode}_AK8_Xbbtagging", f"corr{hist_mode}_AK4_btagging_light_correlated", f"corr{hist_mode}_AK4_btagging_light_uncorrelated", f"corr{hist_mode}_AK4_btagging_heavy_correlated", f"corr{hist_mode}_AK4_btagging_heavy_uncorrelated", "TopPtWeight"]
all_systs = ["Pdfweight", "QCDScaleWeight", "PileUp_Corr"]
years = ["2024"]

n_syst = len(all_systs)
q, r = divmod(n_syst, args.ngroup)
#args.igroup starts with 1
if args.igroup <= r:
    i_start = (q+1)*(args.igroup - 1)
    i_end = i_start + q + 1
else:
    i_start = (q+1) * r + q * (args.igroup - r - 1)
    i_end = i_start + q  

n_syst = len(all_systs)
q, r = divmod(n_syst, args.ngroup)
#args.igroup starts with 1
if args.igroup <= r:
    i_start = (q+1)*(args.igroup - 1)
    i_end = i_start + q + 1
else:
    i_start = (q+1) * r + q * (args.igroup - r - 1)
    i_end = i_start + q

systs = ["nominal"]
for i in range(i_start, i_end):
    systs.append(all_systs[i] + "_up")
    systs.append(all_systs[i] + "_down")

    
print(systs,len(systs))

processes = { "MC_TTBarJets": ["*"], "MC_WJets": ["*"], "MC_QCDJets": ["*"], "MC_DYJets": ["*"], "MC_SingleTopJets":["*"], "MC_TTHJets_Hto2B": ["*"], "MC_TTHJets_Hto2C": ["*"], "MC_TTHJets_Hto2G": ["*"], "MC_TTZJets_ZtoQQ":["*"], "MC_TTTT": ["*"], "MC_TTLL_MLL50":["*"], "MC_TTH_TTToAll_HToAATo4B_M30": ["*"] }
for process in processes:
    if processes[process] == ["*"]:
        processes[process] = []
        if "MC" in process:
            for subprocess in Xsec_json[process]:
                processes[process].append(subprocess) 
print(processes)

def correlated_syst(syst):
    if syst == "nominal" or "Pdfweight" in syst or "QCDScaleWeight" in syst or "TopPtWeight" in syst or "_correlated" in syst:
        return True
    if "JES" in syst and "_202" not in syst:
        return True
    else:
        return False
def relevant_syst(syst, year, process = "MC"):
    if "202" in syst and year + "_" not in syst:
        return False
    if process == "Data" and syst != "nominal":
        return False
    return True



regions = ["Pass", "Fail"]
years = ["2024"]
bins = array.array("d", np.linspace(0, 5000, 501) )
hist_base = ROOT.TH1D(f"Mass_AFJ", f"Mass_AFJ", len(bins) - 1, bins)
hists = {}


for year in years:
    hists[year] = {}
    hists[year]["Data"] = {}
    for region in regions:
        hists[year]["Data"][region] = {}
        syst = "nominal"
        hists[year]["Data"][region][syst] = hist_base.Clone(f"{year}__Data__{Reg}_{region}__{syst}")
    
    for process in processes:
        hists[year][process] = {}        
        for region in regions:
            hists[year][process][region] = {}
            for syst in systs:
                if not relevant_syst(syst, year): continue 
                if correlated_syst(syst): 
                    hists[year][process][region][syst] = hist_base.Clone(f"{year}__{process}__{Reg}_{region}__{syst}")
                else:
                    hists[year][process][region][syst] = hist_base.Clone(f"{year}__{process}__{Reg}_{region}__Y{year}_{syst}")
#print(hists)
processes["Data"] = {}
for f_name in template_files:
    for year in years:
        if (year + "__") in f_name:
            for process in processes:
                if process in f_name:
                    good = 0
                    if "MC" in process:
                        for subprocess in processes[process]:
                            if subprocess in f_name:
                                good = 1
                                break
                    else:
                        good = 1
                    if good == 0:
                        continue
                    print(f_name)
                    f = ROOT.TFile.Open(f_name, "READ")
                    for key in f.GetListOfKeys():
                        hist = key.ReadObj()
                        if isinstance(hist, ROOT.TH1):  
                            hist_name = hist.GetName()
                            print(hist_name) 
                            loaded = 0
                            for region in regions:
                                if region in hist_name:
                                    for syst in systs:
                                        if not relevant_syst(syst, year, process): continue
                                        if hist_name.endswith(syst):
                                            print(f"{year}_{process}_{Reg}_{region}_{syst}")
                                            if "MC" in process:
                                                for subprocess in processes[process]:
                                                    
                                                    if subprocess  + "_" in f_name:
                                                        hists[year][process][region][syst].Add(hist)
                                                        loaded = 1
                                                        break
                                                    
                                            else:
                                                hists[year][process][region][syst].Add(hist)
                                                loaded = 1
                                    print(f"HIST LOADING STATUS:  {loaded}")
                        del hist
                    f.Close()
                    del f

hists_allyears = {}
for process in hists[years[0]]:
    hists_allyears[process] = {}        
    for region in regions:
        hists_allyears[process][region] = {}
        for syst in systs:
            if correlated_syst(syst): 
                if not relevant_syst(syst, "", process): continue
                hists_allyears[process][region][syst] = hist_base.Clone(f"Allyears__{process}__{Reg}_{region}__{syst}")
            else:
                for year in years:
                    if not relevant_syst(syst, year, process): continue
                    syst_byyear = f"Y{year}_{syst}"
                    hists_allyears[process][region][syst_byyear] = hist_base.Clone(f"Allyears__{process}__{Reg}_{region}__{syst_byyear}")
        for syst_byyear in hists_allyears[process][region]:
            for year in years:
                if correlated_syst(syst_byyear): 
                    hists_allyears[process][region][syst_byyear].Add(hists[year][process][region][syst_byyear])
                else:
                    year_syst = syst_byyear.partition("_")[0][1:]
                    root_syst = syst_byyear[(len(year_syst) + 2):]
                    if year_syst not in years:
                        raise ValueError;
                    if year == year_syst:
                        hists_allyears[process][region][syst_byyear].Add(hists[year][process][region][root_syst])
                    else:
                        hists_allyears[process][region][syst_byyear].Add(hists[year][process][region]["nominal"])


open_method = "RECREATE" if args.igroup <= 1 else "UPDATE"
f = ROOT.TFile.Open(f"Templates/Templates_{args.Reg}_all.root", open_method)
f.cd()


for year in years:
    for process in hists[year]:
        for region in regions:
            for syst in hists[year][process][region]:
                if syst == "nominal" and args.igroup > 1: continue
                hists[year][process][region][syst].Write()

for process in hists_allyears:
    for region in hists_allyears[process]:
        for syst in hists_allyears[process][region]:
            if syst == "nominal" and args.igroup > 1: continue
            hists_allyears[process][region][syst].Write()

f.Close()


   


    
