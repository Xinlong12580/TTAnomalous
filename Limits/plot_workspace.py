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
import math
with open(DIR_TOP + "raw_nano/color_scheme.json", "r") as f:
    color_json = json.load(f)
with open(DIR_TOP + "raw_nano/Luminosity.json", "r") as f:
    lumi_json = json.load(f)


from argparse import ArgumentParser
import os

#Reading input args
parser=ArgumentParser()
parser.add_argument('--sig', type=str, dest='sig',action='store', default="MC_TTHJets_Hto2B")
parser.add_argument('--year', type=str, dest='year',action='store', default="2024")
args = parser.parse_args()

use_Asimov_data = True

input_file = "shapes_clean.root"

f = ROOT.TFile.Open(input_file, "READ")
if use_Asimov_data:
    data = f.Get("Pass_prefit/TotalBkg")
else:
    data = f.Get("Pass_prefit/data_obs")
TotalBkg = f.Get("Pass_postfit/TotalBkg")


hists = {}

postfit_dir = f.Get("Pass_postfit")

for key in postfit_dir.GetListOfKeys():
    name = key.GetName()
    if name.startswith("MC"):
        hists[name] = f.Get(f"Pass_postfit/{name}")


mplhep.style.use("CMS")
Signal_processes = {args.sig }
Signal_process = args.sig 
save_dir = "plots/postfit"
os.makedirs(save_dir, exist_ok=True)

bin_centers = []
data_contents = []
data_errors = []
pulls = []
TotalBkg_up = []
TotalBkg_down = []
nbins = TotalBkg.GetNbinsX()
bin_edges = []

for i in range(1, nbins + 1):
    content_data = data.GetBinContent(i)
    error_data = math.sqrt(content_data)
    data_contents.append(content_data)
    data_errors.append(error_data)
    content_TotalBkg = TotalBkg.GetBinContent(i)
    error_TotalBkg = TotalBkg.GetBinError(i)
    error = math.sqrt(error_data**2 + error_TotalBkg**2)
    TotalBkg_up.append(content_TotalBkg + error_TotalBkg )
    TotalBkg_down.append(content_TotalBkg - error_TotalBkg )
    pulls.append((content_data - content_TotalBkg)/ (max(error, 1e-6)))
    bin_edges.append(TotalBkg.GetBinLowEdge(i))
    bin_centers.append(TotalBkg.GetBinCenter(i))

bin_edges.append(TotalBkg.GetXaxis().GetBinUpEdge(nbins))
#-------------------------------Ploting -----------------------------------------------------------

year = args.year
colors = []
labels = []
hs = []
for process in hists:
    if process in Signal_processes: continue
    print(year) 
    colors.append(color_json[process])
    labels.append(process)
    hs.append(hists[process])
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

mplhep.histplot(
    hs,
    label = labels,
    color = colors,
    stack = True,
    histtype = "fill",
    ax = ax1,
)
mplhep.histplot(
    hs ,
    stack = True,  # Note: keep stack=True so contours align with total stacks
    histtype = "step",
    color = "black",
    ax = ax1,
    linewidth = 1.2,
)
ax1.errorbar(bin_centers, data_contents, yerr=data_errors, fmt='o', color='black', label='Data')
mplhep.histplot(
    hists[Signal_process],
    histtype="step",
    yerr=False,
    color=color_json[Signal_process],
    label=Signal_process,
    ax=ax1,
)
bkg_up = np.asarray(TotalBkg_up)
bkg_down = np.asarray(TotalBkg_down)
ax1.stairs(
    bkg_up,
    bin_edges,
    baseline=bkg_down,
    fill=True,
    color="black",
    alpha=0.2,
    linewidth=0,
    label="Post-fit bkg. unc.",
)
mplhep.cms.label("Preliminary", data = False, rlabel = f"{((lumi_json[year])/1000):.2f}"  + r"$fb^{-1}$, "+ year + "(13.6 TeV)", ax = ax1)
ax1.set_ylabel("Event Counts")
ax1.set_xlabel("")
ax1.legend()
ax2.errorbar(bin_centers, pulls, yerr=np.ones_like(pulls), fmt='o', color='black')
ax2.axhline(y = 0, linestyle = '--', color = 'red', linewidth = 1.5)
ax2.set_ylabel("Pulls")
ax2.set_ylim(-3, 3)
ax2.set_xlabel("Mass_AFJ[GeV]")
fig.suptitle(f"Post fit for {Signal_process} of year {year}, with {'Asimov data' if use_Asimov_data else 'observed data'}", fontsize=18, y=0.995)
fig.tight_layout()
ax1.set_yscale("linear")
ax1.set_ylim(auto = True)
fig.savefig(f"{save_dir}/linear_stack.png")
ax1.set_yscale("log")
ax1.set_ylim(0.001,1000)
fig.savefig(f"{save_dir}/stack.png")
plt.close()

