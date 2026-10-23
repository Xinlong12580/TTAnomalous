#dasgoclient -query 'dataset=/TTto*/lpcpfnano*DAZSLE_PFNano*/USER instance=prod/phys03' > MC_TTBarJets_DAZSLE.txt
dasgoclient -query 'dataset=/QCD*/lpcpfnano*DAZSLE_PFNano*/USER instance=prod/phys03' > MC_QCDJets_base.txt
#dasgoclient -query 'dataset=/JetMET*/lpcpfnano*DAZSLE_PFNano*/USER instance=prod/phys03' > Data_DAZSLE.txt
dasgoclient -query '/EGamma*/Run202*-NanoAODv15*/NANOAOD' > Data_2022and2023.txt
dasgoclient -query '/EGamma*/Run2024*MINIv6NANOv15*/NANOAOD' > Data_2024.txt
dasgoclient -query '/Muon/Run202*-NanoAODv15*/NANOAOD' >> Data_2022and2023.txt
dasgoclient -query '/Muon0/Run202*-NanoAODv15*/NANOAOD' >> Data_2022and2023.txt
dasgoclient -query '/Muon0/Run2024*MINIv6NANOv15*/NANOAOD' >> Data_2024.txt
dasgoclient -query '/Muon1/Run202*-NanoAODv15*/NANOAOD' >> Data_2022and2023.txt
dasgoclient -query '/Muon1/Run2024*MINIv6NANOv15*/NANOAOD' >> Data_2024.txt
dasgoclient -query '/JetMET*/Run202*-NanoAODv15*/NANOAOD' >> Data_2022and2023.txt
dasgoclient -query '/JetMET*/Run2024*MINIv6NANOv15*/NANOAOD' >> Data_2024.txt
dasgoclient -query 'dataset=/TTto*_TuneCP5_13p6TeV_powheg-pythia8/*NanoAODv15-150X_mcRun3_*_realistic*/NANOAODSIM' > MC_TTBarJets_base.txt
dasgoclient -query 'dataset=/QCD-4Jet*/RunIII2024Summer24NanoAODv15-150X_mcRun3_2024_realistic_v2*/NANOAODSIM' > MC_QCDJets_2024.txt
dasgoclient -query 'dataset=/TTH-Hto2B_Par-M-125*/*v15*/NANOAODSIM' > MC_TTHJets_2024.txt
dasgoclient -query 'dataset=/TTH_Hto2B_M-125*/*/NANOAODSIM' > MC_TTHJets_base.txt
dasgoclient -query 'dataset=/*toLNu-t-channel-4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8/*2024*-150X*/NANO*' > MC_SingleTopJets_2024.txt
dasgoclient -query 'dataset=/*toLNu-t-channel-4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8/*2022**/NANO*' > MC_SingleTopJets_base.txt
dasgoclient -query 'dataset=/*toLNu-t-channel-4FS_TuneCP5_13p6TeV_powheg-madspin-pythia8/*2023**/NANO*' >> MC_SingleTopJets_base.txt
dasgoclient -query 'dataset=/T*W*toLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/*AODv15-1*/NANO*' >> MC_SingleTopJets_base.txt
dasgoclient -query 'dataset=/T*W*to2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/*AODv15-1*/NANO*' >> MC_SingleTopJets_base.txt
dasgoclient -query 'dataset=/WtoLNu-4Jets_Bin-HT-*-MLNu-*_TuneCP5_13p6TeV_madgraphMLM-pythia8/*/NANO*' > MC_WJets_base.txt
dasgoclient -query 'dataset=/DYto2L-4Jets_Bin-HT-*-MLL-*_TuneCP5_13p6TeV_madgraphMLM-pythia8/*/NANO*' > MC_DYJets_base.txt
dasgoclient -query 'dataset=/Zto2Q*4Jets*/*24*/NANO*' > MC_ZJets_base.txt
dasgoclient -query 'dataset=/TTH-Hto2B_Par-M-125*/*v15*/NANOAODSIM' > MC_TTHJets_Hto2B_2024.txt
dasgoclient -query 'dataset=/TTH-Hto2C_Par-M-125*/*v15*/NANOAODSIM' > MC_TTHJets_Hto2C_2024.txt
dasgoclient -query 'dataset=/TTH-Hto2G_Par-M-125*/*v15*/NANOAODSIM' > MC_TTHJets_Hto2G_2024.txt
dasgoclient -query 'dataset=/TTZ-ZtoQQ-1Jets*/*v15*/NANOAODSIM' > MC_TTZJets_ZtoQQ_2014.txt
dasgoclient -query 'dataset=/TTH-TTToAll-HToAATo4B_Par-M-30*/*v15*/NANOAODSIM' > MC_TTH_TTToAll_HToAATo4B_M30_2024.txt
dasgoclient -query 'dataset=/TTLL_Bin-MLL-50_TuneCP5_13p6TeV*/*v15*/NANOAODSIM' > MC_TTLL_MLL50_2024.txt
dasgoclient -query 'dataset=/TTTT_TuneCP5_13p6TeV_amcatnlo-pythia8*/*v15*/NANOAODSIM' > MC_TTTT_2024.txt



