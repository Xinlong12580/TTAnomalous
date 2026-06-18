rm outputList/*RegVal*
rm outputList/*RegSig*
rm outputList/*Reg*
rm outputList/*
mkdir -p outputList

#collect all output root files belonging to the same dataset
classify_files(){
    input_dir=$1
    output_prefix=$2
    files=$( eosls $input_dir )
    prefix=$eosprefix$input_dir/
    declare -A classified_files
    for file in ${files[@]}; do
        if [[ $file == *"Templates"* || $file == *"output.log"* ]]; then
            continue
        fi
        if [[ $output_prefix == *DIVISION* &&  $file != *"SR1"*"nom"*"2022EE"*"Signal"* ]]; then
            continue
        fi
        if [[ $file = *.txt* ]]; then
            file_base="${file%%.txt*}"
        else
            file_base="${file%%_n-*.root*}"
        fi
        
        classified_files["$file_base"]="${classified_files["$file_base"]} $prefix$file"
    done
    
    for file_base in ${!classified_files[@]}; do
        echo Generating outputList/"$output_prefix"_"$file_base".txt
        
        echo "${classified_files[$file_base]}" | sed 's/^ *//' | tr ' ' '\n' > outputList/"$output_prefix"_"$file_base".txt
    done
}
#classify_files "/store/user/$USER/XHY4bRun3_skim" "SKIM" 


#collecting all output files

skim_dir=/store/user/$USER/TTAnomalous/skim/
eosls $skim_dir > outputList/output_skim_tmp.txt
sed "s@^@root://cmseos.fnal.gov/$skim_dir@" outputList/output_skim_tmp.txt > outputList/output_skim.txt
rm outputList/*tmp*


skim_dir=/store/user/$USER/TTAnomalous/quick_selection/
eosls $skim_dir > outputList/output_skim_tmp.txt
sed "s@^@root://cmseos.fnal.gov/$skim_dir@" outputList/output_skim_tmp.txt > outputList/output_quick_selection.txt
rm outputList/*tmp*
