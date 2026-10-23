#Running division for mode 1p1
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
args = parser.parse_args()
ana = TTAnomalous_Analyzer(args.dataset, args.year, args.n_files, args.i_job)

regions = ["Pass", "Fail"]

file_basename=os.path.basename(args.dataset).replace(".txt", f"_n-{args.n_files}_i-{args.i_job}.root")


    
ana.define_regions("Tagger_AFJ", "0.89")
veto_base_node = ana.analyzer.GetActiveNode()
ana.output = "division_" + file_basename
f = ROOT.TFile.Open("Templates_" + ana.output, "RECREATE")
for region in regions:
    ana.analyzer.SetActiveNode(veto_base_node)
    ana.divide(region)
    print(ana.output)
    ana.dumpTemplates(region, f, "nom",  axis = "Mass_AFJ",  bins = array.array("d", np.linspace(0, 5000, 501)) )
f.Close()
ana.save_cutflowInfo()


