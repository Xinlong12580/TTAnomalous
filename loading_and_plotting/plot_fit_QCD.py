import numpy as np
import ROOT
import matplotlib.pyplot as plt
print("TEST")
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
ROOT.gROOT.SetBatch(True)
with open("pkls/hists_division_TH.pkl", "rb") as f:
    hists = pickle.load(f)

MJY_bins = array.array("d", np.array([ 60, 100, 140, 200, 300, 500]) )
MJJ_bins = array.array("d", np.linspace(0, 4000, 101) )
h_base = ROOT.TH2D("Mass", "MJJ vs MJY", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins) 
h_base_projx = h_base.ProjectionX("MassJY")
h_base_projy = h_base.ProjectionY("MassJJ")
nbins_x = len(MJY_bins) - 1
nbins_y = len(MJJ_bins) - 1

x_edges = np.array(MJY_bins)
y_edges = np.array(MJJ_bins)
h_data = hists["data"]
h_BKGs = hists["BKGs"]

#######################################################################################################################
#--------------------------rebinning  and creating projection hists--------------------------------------------------------------------------------
######################################################################################################################
h_data_rebinned = {}
h_data_rebinned_projx = {}
h_data_rebinned_projy = {}
h_BKGs_rebinned = {}
h_BKGs_rebinned_projx = {}
h_BKGs_rebinned_projy = {}
for year in h_data:
    h_data_rebinned[year] = {}
    h_data_rebinned_projx[year] = {}
    h_data_rebinned_projy[year] = {}
    for region in h_data[year]:
        h_data_rebinned[year][region] = rebin_TH2(h_data[year][region], MJY_bins, MJJ_bins)
        #h_data_rebinned[year][region] = h_data[year][region]
        h_data_rebinned_projx[year][region] = h_data_rebinned[year][region].ProjectionX(f"projx_data_{year}_{region}")
        h_data_rebinned_projy[year][region] = h_data_rebinned[year][region].ProjectionY(f"projy_data_{year}_{region}")

for year in h_BKGs:
    h_BKGs_rebinned[year] = {}
    h_BKGs_rebinned_projx[year] = {}
    h_BKGs_rebinned_projy[year] = {}
    for process in h_BKGs[year]:
        h_BKGs_rebinned[year][process] = {}
        h_BKGs_rebinned_projx[year][process] = {}
        h_BKGs_rebinned_projy[year][process] = {}
        for subprocess in h_BKGs[year][process]:
            h_BKGs_rebinned[year][process][subprocess] = {}
            h_BKGs_rebinned_projx[year][process][subprocess] = {}
            h_BKGs_rebinned_projy[year][process][subprocess] = {}
            for region in h_BKGs[year][process][subprocess]:
                h_BKGs_rebinned[year][process][subprocess][region] = rebin_TH2(h_BKGs[year][process][subprocess][region], MJY_bins, MJJ_bins)
                #h_BKGs_rebinned[year][process][subprocess][region] = h_BKGs[year][process][subprocess][region]
                h_BKGs_rebinned_projx[year][process][subprocess][region] = h_BKGs_rebinned[year][process][subprocess][region].ProjectionX(f"projx_MC_{year}_{process}_{subprocess}_{region}")
                h_BKGs_rebinned_projy[year][process][subprocess][region] = h_BKGs_rebinned[year][process][subprocess][region].ProjectionY(f"projy_MC_{year}_{process}_{subprocess}_{region}") 


############################################################################################################################
#--------------------------merging subprocesses------------------------------------------------------------------------------
#####################################################################################################################


h_BKGs_rebinned_merged = {}
h_BKGs_rebinned_projx_merged = {}
h_BKGs_rebinned_projy_merged = {}
for year in h_BKGs_rebinned:
    h_BKGs_rebinned_merged[year] = {}
    h_BKGs_rebinned_projx_merged[year] = {}
    h_BKGs_rebinned_projy_merged[year] = {}
    for process in h_BKGs_rebinned[year]:
        h_BKGs_rebinned_merged[year][process] = {}
        h_BKGs_rebinned_projx_merged[year][process] = {}
        h_BKGs_rebinned_projy_merged[year][process] = {}
        for region in h_data[year]:
            h_BKGs_rebinned_merged[year][process][region] = h_base.Clone("mergingSubprocess_MC_{year}_{process}_{region}")
            h_BKGs_rebinned_projx_merged[year][process][region] = h_base_projx.Clone("mergingSubprocess_projx_MC_{year}_{process}_{region}")
            h_BKGs_rebinned_projy_merged[year][process][region] = h_base_projy.Clone("mergingSubprocess_projy_MC_{year}_{process}_{region}")
            print(process)
            for subprocess in h_BKGs_rebinned[year][process]:
                h_BKGs_rebinned_merged[year][process][region].Add(h_BKGs_rebinned[year][process][subprocess][region])
                h_BKGs_rebinned_projx_merged[year][process][region].Add(h_BKGs_rebinned_projx[year][process][subprocess][region])
                h_BKGs_rebinned_projy_merged[year][process][region].Add(h_BKGs_rebinned_projy[year][process][subprocess][region])

##########################################################################################################################
#--------------------------------------fitting R_p/f------------------------------------------------------------------------
###################################################################################################################
h_netQCD_VS4_MJY_all = h_base_projx.Clone("h_netQCD_VS4_MJY_all")
h_netQCD_VB2_MJY_all = h_base_projx.Clone("h_netQCD_VB2_MJY_all")
for year in h_data:
    h_netQCD_VS4_MJY =  h_data_rebinned_projx[year]["VS4"].Clone(f"h_netQCD_VS4_MJY_{year}") 
    h_netQCD_VS4_MJY.Add(h_BKGs_rebinned_projx_merged[year]["MC_TTBarJets"]["VS4"], -1)
    h_netQCD_VB2_MJY =  h_data_rebinned_projx[year]["VB2"].Clone(f"h_netQCD_VB2_MJY_{year}") 
    h_netQCD_VB2_MJY.Add(h_BKGs_rebinned_projx_merged[year]["MC_TTBarJets"]["VB2"], -1)
    h_netQCD_VS4_MJY_all.Add(h_netQCD_VS4_MJY)
    h_netQCD_VB2_MJY_all.Add(h_netQCD_VB2_MJY)
    h_ratio_VS4_VB2 = h_netQCD_VS4_MJY.Clone(f"h_ratio_VS4_VB2_{year}")
    h_ratio_VS4_VB2.Divide(h_netQCD_VB2_MJY)
    h_ratio_VS4_VB2.SetTitle(h_ratio_VS4_VB2.GetName())
    c = ROOT.TCanvas()
    fit_func = ROOT.TF1("fit_func", "pol2", 0, 1000)
    fit_result = h_ratio_VS4_VB2.Fit(fit_func, "S")
    h_ratio_VS4_VB2.SetMinimum(-0.02)
    h_ratio_VS4_VB2.SetMaximum(0.05)
    h_ratio_VS4_VB2.Draw("E")  
    fit_func.SetLineColor(ROOT.kRed)
    fit_func.Draw("SAME")
    c.Update()
    c.SaveAs(f"plots/VS4_VB2_fit/fitted_{year}_{h_ratio_VS4_VB2.GetName()}.png")

h_ratio_VS4_VB2 = h_netQCD_VS4_MJY_all.Clone("h_ratio_VS4_VB2_all")
h_ratio_VS4_VB2.Divide(h_netQCD_VB2_MJY_all)
h_ratio_VS4_VB2.SetTitle(h_ratio_VS4_VB2.GetName())
c = ROOT.TCanvas()
fit_func = ROOT.TF1("fit_func", "pol2", 0, 1000)
fit_result = h_ratio_VS4_VB2.Fit(fit_func, "S")
h_ratio_VS4_VB2.SetMinimum(-0.02)
h_ratio_VS4_VB2.SetMaximum(0.05)
h_ratio_VS4_VB2.Draw("E")
fit_func.SetLineColor(ROOT.kRed)
fit_func.Draw("SAME")
c.Update()
c.SaveAs(f"plots/VS4_VB2_fit/fitted_all_{h_ratio_VS4_VB2.GetName()}.png")
