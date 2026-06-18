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
exit
file_name=$1
if [[ X$file_name == "X" ]] ; then
    file_name="signal_XHY4b_Base.json"
fi
> $file_name
echo "{" >> $file_name
for year in ${years[@]}; do
    echo "    \"$year\":" >> $file_name
    echo "    {" >> $file_name
    echo "        \"SignalMC_XHY4b\":" >> $file_name
    echo "        [" >> $file_name
    
    sed 's@^@            "@; s@$@",@' signal_"$year".txt >> $file_name
    truncate -s -2 $file_name
    echo >> $file_name
    echo "        ]" >> $file_name
    echo "    }," >> $file_name
    echo -e "\n\n\n\n" >> $file_name
done
truncate -s -7 $file_name
echo >> $file_name
echo "}" >> $file_name
