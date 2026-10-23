# Running selection for mode 1p1
import ROOT
from TIMBER.Tools.Common import CompileCpp, OpenJSON
from TTAnomalous_Analyzer import *
from argparse import ArgumentParser
import os

#Reading input args
parser=ArgumentParser()
parser.add_argument('-d', type=str, dest='dataset',action='store', required=True)
parser.add_argument('-y', type=str, dest='year',action='store', required=True)
parser.add_argument('-n', type=int, dest='n_files',action='store', required=True)
parser.add_argument('-i', type=int, dest='i_job',action='store', required=True)
parser.add_argument('-s', type=str, dest='JME_syst',action='store', required=True)
parser.add_argument('-r', type=str, dest='region',action='store', required=True)
args = parser.parse_args()

CompileCpp("cpp_modules/selection_functions.cc")
#Specifying columns to save
columns = ["n.*", "Mass_.*", "Pt_.*", "Eta_.*", "Phi_.*", "Idx_.*", ".*goodness" "Tagger_.*", "MassHiggs.*", "idx.*", "gen_.*", ".*_matched.*", "Delta_Eta", "Delta_Y", ".*Weight", ".*weight", "MY", "MX", "leadingFatJetPt","leadingFatJetPhi","leadingFatJetEta", "leadingFatJetMsoftdrop", "MassLeadingTwoFatJets", "MassHiggsCandidate", "PtHiggsCandidate", "EtaHiggsCandidate", "PhiHiggsCandidate", "MassYCandidate", "PtYCandidate", "EtaYCandidate", "PhiYCandidate", "MJJ", "MJY", "PNet_H", "PNet_Y", "weight.*",  "FatJet_pt_JER__up", "PileUp_Corr__nom", "PileUp_Corr__up", "PileUp_Corr__down", "Pileup_nTrueInt"]

Reg = args.region
ana = TTAnomalous_Analyzer(args.dataset, args.year, args.n_files, args.i_job, nEvents = -1)
ana.selection()
file_basename = os.path.basename(args.dataset).removesuffix(".txt")
ana.output = "Reg" + Reg[0:3] + "_" + args.JME_syst + "_1p1_tagged_selected_" + file_basename + f"_n-{args.n_files}_i-{args.i_job}.root"

if "MC" in args.dataset:
    ana.snapshot(columns + ["genWeight"], saveRunChain = True)
else:
    ana.snapshot(columns, saveRunChain = True)
ana.save_cutflowInfo()


if args.JME_syst != "nom":
    exit()

#Making a bunch of hitograms
bins = {}

bins["Mass_JT"] = array.array("d", np.linspace(0, 1000, 101))

bins["Pt_JT"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )
bins["Pt_JB"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )
bins["Pt_Lep"] = array.array("d", np.linspace(-np.pi, np.pi , 21) )

bins["Eta_JT"] = array.array("d", np.linspace(-3, 3, 21) )
bins["Eta_JB"] = array.array("d", np.linspace(-3, 3, 21) )
bins["Eta_Lep"] = array.array("d", np.linspace(-3, 3, 21) )

bins["Phi_JT"] = array.array("d", np.linspace(0, 5000, 501) )
bins["Phi_JB"] = array.array("d", np.linspace(0, 5000, 501) )
bins["Phi_Lep"] = array.array("d", np.linspace(0, 3000, 301) )

bins["Tagger_JB"] = array.array("d", np.linspace(0, 1, 101) )
bins["Tagger_JT"] = array.array("d", np.linspace(0, 1, 101) )

#Saving the histograms to the "Templates" root file
f = ROOT.TFile("Templates_" + ana.output, "RECREATE")
if "MC" in ana.dataset:
    ana.make_TH1(bins, ["weight_All__nominal"], f)
else:
    ana.make_TH1(bins, [], f)
f.Close()
