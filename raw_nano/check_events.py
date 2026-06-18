import ROOT
file_name = "files/2022_SignalMC_XHY4b_NMSSM_XtoYHto4B_MX-1000_MY-125_TuneCP5_13p6TeV_madgraph-pythia8_Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_v5-v2_NANOAODSIM.txt" 
def get_totalEvents(file_name):
    nTotal = 0
    with open (file_name, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            runs = ROOT.RDataFrame("Runs", line)
            nEvents = runs.Sum("genEventCount").GetValue()
            print(nEvents)
            nTotal += nEvents
    print(nTotal)
    return nTotal
        

