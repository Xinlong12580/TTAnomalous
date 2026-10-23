import ROOT
from argparse import ArgumentParser
from TTAnomalous_Helper import *
import array
parser=ArgumentParser()
parser.add_argument('-f', type=str, dest='f', action='store', required=True)
parser.add_argument('--year', type=str, dest='year', action='store', required=True)
parser.add_argument('--recreate',  action='store_true')
args = parser.parse_args()
bins = array.array("d", [0,  50, 100, 150, 200, 300, 400,  600, 800, 1000, 1500, 2000] )

f = ROOT.TFile.Open(args.f, "READ")

print("REBINNING###############################################################")
open_method = "RECREATE" if args.recreate else "UPDATE"
f_out = ROOT.TFile.Open(args.f.replace(".root", "_rebinned.root"), open_method)
for key in f.GetListOfKeys():
    if not key.GetName().startswith(args.year + "__"): continue
    hist = key.ReadObj()
    print("rebinning ", hist.GetName())
    hist = rebin_TH1(hist,  bins, "rebinned_" + hist.GetName().replace("_up", "Up").replace("_down", "Down"), forceOutputPositive = True, outputFloor = 0)
    hist.SetDirectory(f_out)
    hist.Write()


f.Close()
f_out.Close()
