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
with open("pkls/hists_division_2p1_TH.pkl", "rb") as f:
    hists = pickle.load(f)
with open(DIR_TOP + "raw_nano/color_scheme.json", "r") as f:
    color_json = json.load(f)

MJY_bins = array.array("d", np.linspace(0, 2000, 101) )
MJJ_bins = array.array("d", np.linspace(0, 4000, 401) )
MJY_bins = array.array("d", np.array([40, 80, 120, 160, 200, 300, 400, 500, 600, 700, 800, 900,1000,1100,1200,1300, 1400, 1600, 2000, 3000, 4000, 5000]) )
MJJ_bins = array.array("d", np.array([300, 400, 500, 600, 700, 800,900,1000,1100,1200,1300,1400,1600,2000,3000,4000, 5000]) )
h_base = ROOT.TH2D("Mass", "MJJ vs MJY", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins) 
h_base_projx = h_base.ProjectionX("MassJY")
h_base_projy = h_base.ProjectionY("MassJJ")
nbins_x = len(MJY_bins) - 1
nbins_y = len(MJJ_bins) - 1

x_edges = np.array(MJY_bins)
y_edges = np.array(MJJ_bins)
h_data = hists["data"]
h_BKGs = hists["BKGs"]
save_dir = "plots/plots_division_2p1_TH"
#######################################################################################################################
#--------------------------rebinning  and creating projection hists--------------------------------------------------------------------------------
######################################################################################################################
h_data_rebinned = {}
h_data_rebinned_projx = {}
h_data_rebinned_projy = {}
h_BKGs_rebinned = {}
h_BKGs_rebinned_projx = {}
h_BKGs_rebinned_projy = {}
for region in h_data:
    h_data_rebinned[region] = {}
    h_data_rebinned_projx[region] = {}
    h_data_rebinned_projy[region] = {}
    for year in h_data[region]:
        h_data_rebinned[region][year] = rebin_TH2(h_data[region][year]["MJJvsMJY"], MJY_bins, MJJ_bins)
        #h_data_rebinned[region][year] = h_data[region][year]
        h_data_rebinned_projx[region][year] = h_data_rebinned[region][year].ProjectionX(f"projx_data_{year}_{region}")
        h_data_rebinned_projy[region][year] = h_data_rebinned[region][year].ProjectionY(f"projy_data_{year}_{region}")

for region in h_BKGs:
    h_BKGs_rebinned[region] = {}
    h_BKGs_rebinned_projx[region] = {}
    h_BKGs_rebinned_projy[region] = {}
    for year in h_BKGs[region]:
        h_BKGs_rebinned[region][year] = {}
        h_BKGs_rebinned_projx[region][year] = {}
        h_BKGs_rebinned_projy[region][year] = {}
        for process in h_BKGs[region][year]:
            h_BKGs_rebinned[region][year][process] = {}
            h_BKGs_rebinned_projx[region][year][process] = {}
            h_BKGs_rebinned_projy[region][year][process] = {}
            for subprocess in h_BKGs[region][year][process]:
                h_BKGs_rebinned[region][year][process][subprocess] = rebin_TH2(h_BKGs[region][year][process][subprocess]["MJJvsMJY"], MJY_bins, MJJ_bins)
                h_BKGs_rebinned_projx[region][year][process][subprocess] = h_BKGs_rebinned[region][year][process][subprocess].ProjectionX(f"projx_MC_{year}_{process}_{subprocess}_{region}")
                h_BKGs_rebinned_projy[region][year][process][subprocess] = h_BKGs_rebinned[region][year][process][subprocess].ProjectionY(f"projy_MC_{year}_{process}_{subprocess}_{region}")


############################################################################################################################
#--------------------------merging subprocesses------------------------------------------------------------------------------
#####################################################################################################################


h_BKGs_rebinned_merged = {}
h_BKGs_rebinned_projx_merged = {}
h_BKGs_rebinned_projy_merged = {}
for region in h_BKGs_rebinned:
    h_BKGs_rebinned_merged[region] = {}
    h_BKGs_rebinned_projx_merged[region] = {}
    h_BKGs_rebinned_projy_merged[region] = {}
    for year in h_BKGs_rebinned[region]:
        h_BKGs_rebinned_merged[region][year] = {}
        h_BKGs_rebinned_projx_merged[region][year] = {}
        h_BKGs_rebinned_projy_merged[region][year] = {}
        for process in h_BKGs_rebinned[region][year]:
            h_BKGs_rebinned_merged[region][year][process] = h_base.Clone("mergingSubprocess_MC_{year}_{process}_{region}")
            h_BKGs_rebinned_projx_merged[region][year][process] = h_base_projx.Clone("mergingSubprocess_projx_MC_{year}_{process}_{region}")
            h_BKGs_rebinned_projy_merged[region][year][process] = h_base_projy.Clone("mergingSubprocess_projy_MC_{year}_{process}_{region}")
            print(process)
            for subprocess in h_BKGs_rebinned[region][year][process]:
                h_BKGs_rebinned_merged[region][year][process].Add(h_BKGs_rebinned[region][year][process][subprocess])
                h_BKGs_rebinned_projx_merged[region][year][process].Add(h_BKGs_rebinned_projx[region][year][process][subprocess])
                h_BKGs_rebinned_projy_merged[region][year][process].Add(h_BKGs_rebinned_projy[region][year][process][subprocess])
################################################################################################################################
#-----------------------------------------making 2D plots-------------------------
########################################################################################################################
data_binned_projx = {}
data_binned_error_projx = {}
data_binned_projy = {}
data_binned_error_projy = {}
for region in h_data:
    data_binned_projx[region] = {}
    data_binned_error_projx[region] = {}
    data_binned_projy[region] = {}
    data_binned_error_projy[region] = {}
    for year in h_data[region]:
        data_binned_projx[region][year] = [h_data_rebinned_projx[region][year].GetBinContent(i) for i in range(1, h_data_rebinned_projx[region][year].GetNbinsX() + 1)]
        data_binned_error_projx[region][year] = [h_data_rebinned_projx[region][year].GetBinError(i) for i in range(1, h_data_rebinned_projx[region][year].GetNbinsX() + 1)]
        data_binned_projy[region][year] = [h_data_rebinned_projy[region][year].GetBinContent(i) for i in range(1, h_data_rebinned_projy[region][year].GetNbinsX() + 1)]
        data_binned_error_projy[region][year] = [h_data_rebinned_projy[region][year].GetBinError(i) for i in range(1, h_data_rebinned_projy[region][year].GetNbinsX() + 1)]



h_data_rebinned_all = {}
h_ttbar_rebinned_merged_all = {}
h_netQCD_rebinned_merged_all = {}
h_MCQCD_rebinned_merged_all = {}
h_Signal_rebinned_merged_all = {}
for region in h_data:
    print(region)
    #h_data_rebinned_all[region] = h_base.Clone(f"2DMass_data_all_{region}")
    h_ttbar_rebinned_merged_all[region] = h_base.Clone(f"2DMass_ttbar_all_{region}")
    #h_netQCD_rebinned_merged_all[region] = h_base.Clone(f"2DMass_netQCD_all_{region}")
    h_MCQCD_rebinned_merged_all[region] = h_base.Clone(f"2DMass_MCQCD_all_{region}")
    #h_Signal_rebinned_merged_all[region] = h_base.Clone(f"2DMass_Signal_all_{region}")

for region in h_data:
    for year in h_data[region]:
 
        #h_data_rebinned_all[region].Add(h_data_rebinned[region][year])
        h_ttbar_rebinned_merged_all[region].Add(h_BKGs_rebinned_merged[region][year]["MC_TTBarJets"])
        #h_netQCD = h_data_rebinned[region][year].Clone(f"2DMass_netQCD_{year}_{region}" )
        #h_netQCD.Add(h_BKGs_rebinned_merged[region][year]["MC_TTBarJets"], -1)
        #h_netQCD_rebinned_merged_all[region].Add(h_netQCD)
        h_MCQCD_rebinned_merged_all[region].Add(h_BKGs_rebinned_merged[region][year]["MC_QCDJets"])
        #h_Signal_rebinned_merged_all[region].Add(h_BKGs_rebinned_merged[region][year]["SignalMC_XHY4b"])


        #z_data = np.array([[h_data_rebinned[region][year].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
        z_ttbar = np.array([[h_BKGs_rebinned_merged[region][year]["MC_TTBarJets"].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
        z_MCQCD = np.array([[h_BKGs_rebinned_merged[region][year]["MC_QCDJets"].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
        #z_netQCD = z_data - z_ttbar 
        
        #zs = [z_data, z_ttbar, z_MCQCD, z_netQCD]
        zs = [z_ttbar, z_MCQCD]
        processes = ["ttbar", "MCQCD"] 
        for i in range(len(zs)):
            z = zs[i]
            process = processes[i]
            fig, ax = plt.subplots(figsize=(8, 6))
            mesh = ax.pcolormesh(x_edges, y_edges, z, cmap="viridis")        
            mplhep.cms.text("Simulation WiP", ax = ax)  # Optional CMS-style label
            cbar = fig.colorbar(mesh, ax=ax, label="Entries")
            ax.set_xlabel("MJY")
            ax.set_ylabel("MJJ")
            ax.set_title(f"{year} {process} {region}")
            fig.tight_layout()
            fig.savefig(f"{save_dir}/{year}__{process}__{region}.png")
        for mass in h_BKGs_rebinned[region][year]["SignalMC_XHY4b"]:
            z = np.array([[h_BKGs_rebinned[region][year]["SignalMC_XHY4b"][mass].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
            fig, ax = plt.subplots(figsize=(8, 6))
            mesh = ax.pcolormesh(x_edges, y_edges, z, cmap="viridis")        
            mplhep.cms.text("Simulation WiP", ax = ax)  # Optional CMS-style label
            cbar = fig.colorbar(mesh, ax=ax, label="Entries")
            ax.set_xlabel("MJY")
            ax.set_ylabel("MJJ")
            ax.set_title(f"{year} Signal {mass} {region}")
            fig.tight_layout()
            fig.savefig(f"{save_dir}/{year}__signal__{mass}__{region}.png")
exit()    


for region in h_data_rebinned_all:
    if region not in ["VB1", "VB2", "VS1", "VS2", "VS3", "VS4"]:
        continue
    print(region)


    z_data = np.array([[h_data_rebinned_all[region].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
    z_ttbar = np.array([[h_ttbar_rebinned_merged_all[region].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
    z_netQCD = np.array([[h_netQCD_rebinned_merged_all[region].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
    z_MCQCD = np.array([[h_MCQCD_rebinned_merged_all[region].GetBinContent(ix+1, iy+1) for ix in range(nbins_x)] for iy in range(nbins_y)])
        
    zs = [z_data, z_ttbar, z_MCQCD, z_netQCD]
    processes = ["data", "ttbar", "MCQCD", "netQCD"] 
    for i in range(len(zs)):
        z = zs[i]
        process =   processes[i]
        fig, ax = plt.subplots(figsize=(8, 6))
        mesh = ax.pcolormesh(x_edges, y_edges, z, cmap="viridis") 
        mplhep.cms.text("Simulation Internal", ax=ax)  # Optional CMS-style label
        cbar = fig.colorbar(mesh, ax=ax, label="Entries")
        ax.set_xlabel("MJY")
        ax.set_ylabel("MJJ")
        ax.set_title(f"ALL__{process}__{region}")
        fig.tight_layout()
        fig.savefig(f"{save_dir}/ALL__{process}__{region}.png")


#########################################################################################################################################
#----------------------------------------making stack plots ------------------------------------------------------------------------------------
##############################################################################################################################

for region in h_data:
    if region not in ["VB1", "VB2", "VS1", "VS2", "VS3", "VS4"]:
        continue
    for year in h_data[region]:

        bin_centers_projx = (np.array(MJY_bins)[:-1] + np.array(MJY_bins)[1:])/2
        bin_centers_projy = (np.array(MJJ_bins)[:-1] + np.array(MJJ_bins)[1:])/2
        

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

        #ax1.errorbar(bin_centers_projx, data_binned_projx[region][year], yerr=data_binned_error_projx[region][year], fmt='o', color='black', label='Data')
        mplhep.histplot(
            #[h_BKGs_rebinned_projx_merged[year]["MC_SingleTopJets"][region], h_BKGs_rebinned_projx_merged[year]["MC_DibosonJets"][region], h_BKGs_rebinned_projx_merged[year]["MC_HiggsJets"][region], h_BKGs_rebinned_projx_merged[region][year]["MC_TTBarJets"], h_BKGs_rebinned_projx_merged[year]["MC_WZJets"][region], h_BKGs_rebinned_projx_merged[region][year]["MC_QCDJets"]],
            #label = ["SingleTop", "Diboson", "Higgs", "TTBar", "WZ", "QCD"],
            #color = ["darkblue", "beige", "red", "lightblue", "green", "orange"],
            [h_BKGs_rebinned_projx_merged[region][year]["MC_WZJets"], h_BKGs_rebinned_projx_merged[region][year]["MC_TTBarJets"], h_BKGs_rebinned_projx_merged[region][year]["MC_QCDJets"]],
            label = ["WZ", "TTBar", "QCD"],
            color = [color_json["MC_WZJets"], color_json["MC_TTBarJets"], color_json["MC_QCDJets"]],
            stack = True,
            histtype = "fill",
            ax = ax1,
        )
        mplhep.histplot(
            #[h_BKGs_rebinned_projx_merged[year]["MC_SingleTopJets"][region], h_BKGs_rebinned_projx_merged[year]["MC_DibosonJets"][region], h_BKGs_rebinned_projx_merged[year]["MC_HiggsJets"][region], h_BKGs_rebinned_projx_merged[region][year]["MC_TTBarJets"], h_BKGs_rebinned_projx_merged[year]["MC_WZJets"][region], h_BKGs_rebinned_projx_merged[region][year]["MC_QCDJets"]],
            [h_BKGs_rebinned_projx_merged[region][year]["MC_WZJets"], h_BKGs_rebinned_projx_merged[region][year]["MC_TTBarJets"], h_BKGs_rebinned_projx_merged[region][year]["MC_QCDJets"]],
            stack = True,  # Note: keep stack=True so contours align with total stacks
            histtype = "step",
            color = "black",
            ax = ax1,
            linewidth = 1.2,
        )
        mplhep.cms.label("Preliminary", data = False, rlabel = r"7.9804 $fb^{-1}$, 2022(13.6 TeV)", ax = ax1)
        ax1.set_ylabel("Event Counts")
        ax1.set_xlabel("")
        ax1.legend()
        
        fig.tight_layout()
        ax1.set_yscale("linear")
        ax1.set_ylim(auto = True)
        fig.savefig(f"{save_dir}/linear_stack_projx_{year}_{region}.png")
        ax1.set_yscale("log")
        ax1.set_ylim(1,10000000)
        fig.savefig(f"{save_dir}/stack_projx_{year}_{region}.png")

    
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

        #ax1.errorbar(bin_centers_projy, data_binned_projy[region][year], yerr=data_binned_error_projy[region][year], fmt='o', color='black', label='Data')
        mplhep.histplot(
            [h_BKGs_rebinned_projy_merged[region][year]["MC_WZJets"], h_BKGs_rebinned_projy_merged[region][year]["MC_TTBarJets"], h_BKGs_rebinned_projy_merged[region][year]["MC_QCDJets"]],
            label = ["WZ", "TTBar", "QCD"],
            color = [color_json["MC_WZJets"], color_json["MC_TTBarJets"], color_json["MC_QCDJets"]],
            stack = True,
            histtype = "fill",
            ax = ax1,
        )
        mplhep.histplot(
            #[h_BKGs_rebinned_projy_merged[year]["MC_SingleTopJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_DibosonJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_HiggsJets"][region], h_BKGs_rebinned_projy_merged[region][year]["MC_TTBarJets"], h_BKGs_rebinned_projy_merged[year]["MC_WZJets"][region], h_BKGs_rebinned_projy_merged[region][year]["MC_QCDJets"]],
            [h_BKGs_rebinned_projy_merged[region][year]["MC_WZJets"], h_BKGs_rebinned_projy_merged[region][year]["MC_TTBarJets"], h_BKGs_rebinned_projy_merged[region][year]["MC_QCDJets"]],
            stack = True,  # Note: keep stack=True so contours align with total stacks
            histtype = "step",
            color = "black",
            ax = ax1,
            linewidth = 1.2,
        )
        mplhep.cms.label("Preliminary", data = False, rlabel = r"7.9804 $fb^{-1}$, 2022(13.6 TeV)", ax = ax1)
        ax1.set_ylabel("Event Counts")
        ax1.set_xlabel("")
        ax1.legend()
        
        fig.tight_layout()
        ax1.set_yscale("linear")
        ax1.set_ylim(auto = True)
        fig.savefig(f"{save_dir}/linear_stack_projy_{year}_{region}.png")
        ax1.set_yscale("log")
        ax1.set_ylim(1,10000000)
        fig.savefig(f"{save_dir}/stack_projy_{year}_{region}.png")



for region in h_data:
    if region not in ["SR1", "SR2"]:
        continue
    for year in h_data[region]:

        

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

        mplhep.histplot(
            [h_BKGs_rebinned_projx_merged[region][year]["MC_WZJets"], h_BKGs_rebinned_projx_merged[region][year]["MC_TTBarJets"], h_BKGs_rebinned_projx_merged[region][year]["MC_QCDJets"]],
            label = ["WZ", "TTBar", "QCD"],
            color = [color_json["MC_WZJets"], color_json["MC_TTBarJets"], color_json["MC_QCDJets"]],
            stack = True,
            histtype = "fill",
            ax = ax1,
        )
        mplhep.histplot(
            [h_BKGs_rebinned_projx_merged[region][year]["MC_WZJets"], h_BKGs_rebinned_projx_merged[region][year]["MC_TTBarJets"], h_BKGs_rebinned_projx_merged[region][year]["MC_QCDJets"]],
            stack = True,  # Note: keep stack=True so contours align with total stacks
            histtype = "step",
            color = "black",
            ax = ax1,
            linewidth = 1.2,
        )
        mplhep.cms.label("Preliminary", data = False, rlabel = r"7.9804 $fb^{-1}$, 2022(13.6 TeV)", ax = ax1)
        ax1.set_ylabel("Event Counts")
        ax1.set_xlabel("")
        ax1.legend()
        
        fig.tight_layout()
        ax1.set_yscale("linear")
        ax1.set_ylim(auto = True)
        fig.savefig(f"{save_dir}/linear_stack_projx_{year}_{region}.png")
        ax1.set_yscale("log")
        ax1.set_ylim(1,10000000)
        fig.savefig(f"{save_dir}/stack_projx_{year}_{region}.png")

    
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

        mplhep.histplot(
            #[h_BKGs_rebinned_projy_merged[year]["MC_SingleTopJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_DibosonJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_HiggsJets"][region], h_BKGs_rebinned_projy_merged[region][year]["MC_TTBarJets"], h_BKGs_rebinned_projy_merged[year]["MC_WZJets"][region], h_BKGs_rebinned_projy_merged[region][year]["MC_QCDJets"]],
            #label = ["SingleTop", "Diboson", "Higgs", "TTBar", "WZ", "QCD"],
            #color = ["darkblue", "beige", "red", "lightblue", "green", "orange"],
            [h_BKGs_rebinned_projy_merged[region][year]["MC_WZJets"], h_BKGs_rebinned_projy_merged[region][year]["MC_TTBarJets"], h_BKGs_rebinned_projy_merged[region][year]["MC_QCDJets"]],
            label = ["WZ", "TTBar", "QCD"],
            color = [color_json["MC_WZJets"], color_json["MC_TTBarJets"], color_json["MC_QCDJets"]],
            stack = True,
            histtype = "fill",
            ax = ax1,
        )
        mplhep.histplot(
            #[h_BKGs_rebinned_projy_merged[year]["MC_SingleTopJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_DibosonJets"][region], h_BKGs_rebinned_projy_merged[year]["MC_HiggsJets"][region], h_BKGs_rebinned_projy_merged[region][year]["MC_TTBarJets"], h_BKGs_rebinned_projy_merged[year]["MC_WZJets"][region], h_BKGs_rebinned_projy_merged[region][year]["MC_QCDJets"]],
            [h_BKGs_rebinned_projy_merged[region][year]["MC_WZJets"], h_BKGs_rebinned_projy_merged[region][year]["MC_TTBarJets"], h_BKGs_rebinned_projy_merged[region][year]["MC_QCDJets"]],
            stack = True,  # Note: keep stack=True so contours align with total stacks
            histtype = "step",
            color = "black",
            ax = ax1,
            linewidth = 1.2,
        )
        mplhep.cms.label("Preliminary", data = False, rlabel = r"7.9804 $fb^{-1}$, 2022(13.6 TeV)", ax = ax1)
        ax1.set_ylabel("Event Counts")
        ax1.set_xlabel("")
        ax1.legend()
        
        fig.tight_layout()
        ax1.set_yscale("linear")
        ax1.set_ylim(auto = True)
        fig.savefig(f"{save_dir}/linear_stack_projy_{year}_{region}.png")
        ax1.set_yscale("log")
        ax1.set_ylim(1,10000000)
        fig.savefig(f"{save_dir}/stack_projy_{year}_{region}.png")


for region in h_data:
    if region not in ["SR1", "SR2"]:
        continue
    for year in h_data[region]:

        bin_centers_projx = (np.array(MJY_bins)[:-1] + np.array(MJY_bins)[1:])/2
        bin_centers_projy = (np.array(MJJ_bins)[:-1] + np.array(MJJ_bins)[1:])/2
        

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

        mplhep.histplot(
            [h_BKGs_rebinned_projx[region][year]["SignalMC_XHY4b"]["MX-3000_MY-300"]],
            label = ["WX-3000_MY-300"],
            color = [color_json["SignalMC_XHY4b"]],
            stack = True,
            histtype = "fill",
            ax = ax1,
        )
        mplhep.histplot(
            [h_BKGs_rebinned_projx[region][year]["SignalMC_XHY4b"]["MX-3000_MY-300"]],
            stack = True,  # Note: keep stack=True so contours align with total stacks
            histtype = "step",
            color = "black",
            ax = ax1,
            linewidth = 1.2,
        )
        mplhep.cms.label("Preliminary", data = False, rlabel = r"7.9804 $fb^{-1}$, 2022(13.6 TeV)", ax = ax1)
        ax1.set_ylabel("Event Counts")
        ax1.set_xlabel("")
        ax1.legend()
        
        fig.tight_layout()
        ax1.set_yscale("linear")
        ax1.set_ylim(auto = True)
        fig.savefig(f"{save_dir}/linear_signal_projx_{year}_{region}.png")
        ax1.set_yscale("log")
        ax1.set_ylim(1,10000000)
        fig.savefig(f"{save_dir}/log_signal_{year}_{region}.png")

    
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

        mplhep.histplot(
            [h_BKGs_rebinned_projy[region][year]["SignalMC_XHY4b"]["MX-3000_MY-300"]],
            label = ["WX-3000_MY-300"],
            color = [color_json["SignalMC_XHY4b"]],
            stack = True,
            histtype = "fill",
            ax = ax1,
        )
        mplhep.histplot(
            [h_BKGs_rebinned_projy[region][year]["SignalMC_XHY4b"]["MX-3000_MY-300"]],
            stack = True,  # Note: keep stack=True so contours align with total stacks
            histtype = "step",
            color = "black",
            ax = ax1,
            linewidth = 1.2,
        )
        mplhep.cms.label("Preliminary", data = False, rlabel = r"7.9804 $fb^{-1}$, 2022(13.6 TeV)", ax = ax1)
        ax1.set_ylabel("Event Counts")
        ax1.set_xlabel("")
        ax1.legend()
        
        fig.tight_layout()
        ax1.set_yscale("linear")
        ax1.set_ylim(auto = True)
        fig.savefig(f"{save_dir}/linear_signal_projy_{year}_{region}.png")
        ax1.set_yscale("log")
        ax1.set_ylim(1,10000000)
        fig.savefig(f"{save_dir}/log_signal_projy_{year}_{region}.png")

exit()
##########################################################################################################################
#--------------------------------------fitting R_p/f------------------------------------------------------------------------
###################################################################################################################
h_netQCD_VS4_MJY_all = h_base_projx.Clone("h_netQCD_VS4_MJY_all")
h_netQCD_VB2_MJY_all = h_base_projx.Clone("h_netQCD_VB2_MJY_all")
for year in years:
    h_netQCD_VS4_MJY =  h_data_rebinned_projx["VS4"][year].Clone(f"h_netQCD_VS4_MJY_{year}") 
    h_netQCD_VS4_MJY.Add(h_BKGs_rebinned_projx_merged[year]["MC_TTBarJets"]["VS4"], -1)
    h_netQCD_VB2_MJY =  h_data_rebinned_projx["VB2"][year].Clone(f"h_netQCD_VB2_MJY_{year}") 
    h_netQCD_VB2_MJY.Add(h_BKGs_rebinned_projx_merged[year]["MC_TTBarJets"]["VB2"], -1)
    h_netQCD_VS4_MJY_all.Add(h_netQCD_VS4_MJY)
    h_netQCD_VB2_MJY_all.Add(h_netQCD_VB2_MJY)
    h_ratio_VS4_VB2 = h_netQCD_VS4_MJY.Clone(f"h_ratio_VS4_VB2_{year}")
    h_ratio_VS4_VB2.Devide(h_netQCD_VB2_MJY)
    h_ratio_VS4_VB2.SetTitle(h_ratio_VS4_VB2.GetName())
    c = ROOT.TCanvas()
    fit_func = ROOT.TF1("fit_func", "pol2", 0, 1000)
    fit_result = h_ratio_VS4_VB2.Fit(fit_func, "S")
    h_ratio_VS4_VB2.Draw("E")   
    fit_func.SetLineColor(ROOT.kRed)
    fit_func.Draw("SAME")
    c.Update()
    c.SaveAs(f"plots/VS4_VB2_fit/fitted_{year}_{h.GetName()}.png")

h_ratio_VS4_VB2 = h_netQCD_VS4_MJY_all.Clone("h_ratio_VS4_VB2_all")
h_ratio_VS4_VB2.Devide(h_netQCD_VB2_MJY_all)
h_ratio_VS4_VB2.SetTitle(h_ratio_VS4_VB2_all.GetName())
c = ROOT.TCanvas()
fit_func = ROOT.TF1("fit_func", "pol2", 0, 1000)
fit_result = h_ratio_VS4_VB2.Fit(fit_func, "S")
h_ratio_VS4_VB2.Draw("E")
fit_func.SetLineColor(ROOT.kRed)
fit_func.Draw("SAME")
c.Update()
c.SaveAs(f"plots/VS4_VB2_fit/fitted_all_{h.GetName()}.png")
