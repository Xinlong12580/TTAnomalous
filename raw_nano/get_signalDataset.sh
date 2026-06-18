dasgoclient -query dataset=/NMSSM_XtoYHto4B_MX-*_MY-*_TuneCP5_13p6TeV_madgraph-pythia8/Run3Summer22NanoAODv12-130X_mcRun3_2022_realistic_*/NANOAODSIM > signal_2022.txt
dasgoclient -query dataset=/NMSSM_XtoYHto4B_MX-*_MY-*_TuneCP5_13p6TeV_madgraph-pythia8/Run3Summer22EENanoAODv12-130X_mcRun3_2022_realistic_*/NANOAODSIM > signal_2022EE.txt
dasgoclient -query dataset=/NMSSM_XtoYHto4B_MX-*_MY-*_TuneCP5_13p6TeV_madgraph-pythia8/Run3Summer23NanoAODv12-130X_mcRun3_2023_realistic_*/NANOAODSIM > signal_2023.txt
dasgoclient -query dataset=/NMSSM_XtoYHto4B_MX-*_MY-*_TuneCP5_13p6TeV_madgraph-pythia8/Run3Summer23BPixNanoAODv12-130X_mcRun3_2023_realistic_*/NANOAODSIM > signal_2023BPix.txt
dasgoclient -query dataset=/NMSSM-XtoYHto4B_Par-MX-*-MY-*_TuneCP5_13p6TeV_madgraph-pythia8/RunIII2024*2024*/NANOAODSIM > signal_2024.txt
years=( "2022" "2022EE" "2023" "2023BPix" "2024")
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
