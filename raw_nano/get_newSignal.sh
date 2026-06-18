years=(2022 2022EE 2023 2023BPix)
year=( $1 )
for year in ${years[@]} ; do
    echo $year
    datasets=$( eosls $eospath/XHY4b_regen/mc_$year )
    for dataset in ${datasets[@]}; do
        MX_tmp="${dataset#*MX-}"
        MX="${MX_tmp%%_MY-*}"
        MY_tmp="${dataset#*MY-}"
        MY="${MY_tmp%%_TuneCP5*}"
        root_files=""
        subdir0s=$( eosls $eospath/XHY4b_regen/mc_$year/$dataset )
        count0=0
        for subdir0 in ${subdir0s[@]}; do
            (( count0 ++ ))
            if [[ $count0 == 2 ]]; then
                eosrm -r $eospath/XHY4b_regen/mc_$year/$dataset/$subdir0/
                 break
            fi
            subdir1s=$( eosls $eospath/XHY4b_regen/mc_$year/$dataset/$subdir0 )
            count1=0
            for subdir1 in ${subdir1s[@]}; do
                (( count1 ++ ))
                echo $count1
                if [[ $count1 == 2 ]]; then
                    eosrm -r $eospath/XHY4b_regen/mc_$year/$dataset/$subdir0/$subdir1
                    break
                fi
                subdir2s=$( eosls $eospath/XHY4b_regen/mc_$year/$dataset/$subdir0/$subdir1 )
                for subdir2 in ${subdir2s[@]}; do
                    file_path=$eospath/XHY4b_regen/mc_$year/$dataset/$subdir0/$subdir1/$subdir2
                    root_files_tmp=$( eosls $eospath/XHY4b_regen/mc_$year/$dataset/$subdir0/$subdir1/$subdir2 )
                    for root_file in ${root_files_tmp[@]}; do
                        if [[ $root_file == *.root ]]; then
                            root_files=$root_files$eosprefix$file_path/$root_file" "
                        fi
                    done
                done
            done
        done
        echo $root_files
        if [[ -n "${root_files//[[:space:]]/}" ]]; then
            > files/"$year"__SignalMC_XHY4b__MX-"$MX"_MY-"$MY".txt
            for root_file in ${root_files[@]}; do
                echo $root_file >> files/"$year"__SignalMC_XHY4b__MX-"$MX"_MY-"$MY".txt
            done
        else
            eosrm -r $eospath/XHY4b_regen/mc_$year/$dataset
        fi
    done
    #echo $datasets

done
