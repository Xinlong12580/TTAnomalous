while getopts "y:p:" opt; do
  case $opt in
    y) year="$OPTARG" ;;
    p) process="$OPTARG" ;;
    *) echo "Usage: $0 -y year -p process" >&2; exit 1 ;;
  esac
done
echo $year $process
json_file=Datasets_background_v15.json
if [ $process = "SignalMC_XHY4b" ]; then
    json_file=Datasets_signal_v15.json
elif [ $process = "Data" ]; then
    json_file=Datasets_data_v15.json
fi
readarray -t subprocesses < <(jq -r --arg year "$year" --arg process "$process" '.[$year][$process] | keys[]' $json_file)
> bad_dataset_"$year"_"$process".txt

for subprocess in ${subprocesses[@]}; do
    echo $subprocess
    dataset=$(jq -r --arg year "$year" --arg process "$process" --arg subprocess "$subprocess" '.[$year][$process][$subprocess]' $json_file)     
    echo TRYING TO GET DATASET OF SUBPROCESS: $subprocess FROM $dataset
    if [[ $dataset = *"DAZSLE"* ]]; then
	    Command="file dataset="$dataset' instance=prod/phys03' 
    else
	    Command="file dataset="$dataset
    fi
	data_name=./files_xrootd/"$year"__"$process"__"$subprocess"
	#echo $Command
	echo dasgoclient -query "$Command"
	dasgoclient -query "$Command" > "$data_name"_tmp.txt
    statusflag=$(tail -c 26 "$data_name"_tmp.txt)
    echo X$statusflag
    if [[ X"$statusflag" == "Xunmatched dataset pattern" || X"$statusflag" == "X" ]]; then
	    echo "$data_name" >> bad_dataset_"$year"_"$process".txt
        echo -e "\e[31mGETTING $subprocess FAILED.\e[0m" 
    else
        #sed 's@^@root://cmsxrootd.fnal.gov/@' "$data_name"_tmp.txt | tee -a "$data_name".txt
        sed 's@^@root://cmsxrootd.fnal.gov/@' "$data_name"_tmp.txt > "$data_name".txt
        echo -e "\e[32mGETTING $subprocess SUCCESSFUL.\e[0m" 
	fi
    rm "$data_name"_tmp.txt
done
echo BAD DATASET OF  "$year" "$process":
cat bad_dataset_"$year"_"$process".txt
