# Running skimming and golden json masking

import ROOT
from TIMBER.Tools.Common import CompileCpp, OpenJSON
from TTAnomalous_Analyzer import *
from argparse import ArgumentParser
import os

#Reading Args
parser=ArgumentParser()
parser.add_argument('-d', type=str, dest='dataset',action='store', required=True)
parser.add_argument('-y', type=str, dest='year',action='store', required=True)
parser.add_argument('-n', type=int, dest='n_files',action='store', required=True)
parser.add_argument('-i', type=int, dest='i_job',action='store', required=True)
parser.add_argument('-e', type=int, dest="n_events", action="store", default=-1)
args = parser.parse_args()


CompileCpp("cpp_modules/skim_functions.cc")
CompileCpp("cpp_modules/goldenJson_mask.cc")

ana = TTAnomalous_Analyzer(args.dataset, args.year, args.n_files, args.i_job, args.n_events)

#Running skimming and masking
ana.skim()

ana.mask_goldenJson()
ana.cut_goldenJson()

#Saving snapshot and cutflow
file_basename=os.path.basename(args.dataset)
ana.output = "skimmed_" + file_basename + f"_n-{args.n_files}_i-{args.i_job}.root"
if "Data" in args.dataset:
    ana.output = "masked_skimmed_" + file_basename + f"_n-{args.n_files}_i-{args.i_job}.root"

ana.snapshot(saveRunChain = True)
ana.save_cutflowInfo()
