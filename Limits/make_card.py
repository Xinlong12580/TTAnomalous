import ROOT
import array
ROOT.gROOT.SetBatch(True)
from argparse import ArgumentParser
import os

#Reading input args
parser=ArgumentParser()
parser.add_argument('--sig', type=str, dest='sig',action='store', default="MC_TTHJets_Hto2B")
parser.add_argument('--year', type=str, dest='year',action='store', default="2024")
parser.add_argument('--input_file', type=str, dest='input_file',action='store', default="Templates/Templates_Signal_all_rebinned.root")
args = parser.parse_args()


Hists = {}
bkgs = ["MC_TTBarJets", "MC_SingleTopJets", "MC_WJets", "MC_DYJets", "MC_QCDJets"]

signals = args.sig.split(";")
signal_str = args.sig.replace(";", "__")
systs = ["Pdfweight", "QCDScaleWeight", "Y2024_PileUp_Corr"]
year = args.year
channels = ["Pass"]
input_file = args.input_file

idx = {}
_idx = 1
for bkg in bkgs:
    idx[bkg] = _idx
    _idx += 1
_idx = -1
for signal in signals:
    idx[signal] = _idx
    _idx -= 1
imax = len(channels)
jmax = (len(bkgs) + len(signals)) - 1
kmax = len(systs)




    
####Make combine card #################
with open(f"card.txt", "w") as _f:
    _f.write(f"imax {imax}\n")
    _f.write(f"jmax {jmax}\n")
    _f.write(f"kmax {kmax}\n")
    _f.write("----------------------------------------------\n")
    for channel in channels:
        for process in bkgs:
            _f.write(f"shapes {process} {channel} {input_file} rebinned_{year}__{process}__SR_{channel}__nominal rebinned_{year}__{process}__SR_{channel}__$SYSTEMATIC\n")
        for process in signals:
            _f.write(f"shapes {process} {channel} {input_file} rebinned_{year}__{process}__SR_{channel}__nominal rebinned_{year}__{process}__SR_{channel}__$SYSTEMATIC\n")
        _f.write(f"shapes data_obs {channel} {input_file} rebinned_{year}__Data__SR_{channel}__nominal\n")
    _f.write("----------------------------------------------\n")
    line_bin = "bin"
    line_observation = "observation"
    for channel in channels:
        line_bin += f" {channel}"
        line_observation += " -1"
    _f.write(f"{line_bin}\n")
    _f.write(f"{line_observation}\n")
    _f.write("----------------------------------------------\n")
    channel_ledger = []
    process_ledger = []
    for channel in channels:
        for process in bkgs:
            channel_ledger.append(channel)
            process_ledger.append(process)
        for process in signals:
            channel_ledger.append(channel)
            process_ledger.append(process)
    line_bin = "bin"
    line_process = "process"
    line_process_index = "process"
    line_rate = "rate"
    for i in range(len(channel_ledger)):
        line_bin += f" {channel_ledger[i]}"
        line_process += f" {process_ledger[i]}"
        line_process_index += f" {idx[process_ledger[i]]}"
        line_rate += " -1"        
    _f.write(f"{line_bin}\n")
    _f.write(f"{line_process}\n")
    _f.write(f"{line_process_index}\n")
    _f.write(f"{line_rate}\n")
    _f.write("----------------------------------------------\n")
    for syst in systs:
        if "Y20" in syst and year + "_" not in syst:
            print(f"Warning: systematic {syst} is not defined in year {year}. Skip")
            continue
        line_syst = f"{syst} shape"
        for i in range(len(channel_ledger)):
            line_syst += f" {1.0}"
        _f.write(f"{line_syst}\n")



#######################################






