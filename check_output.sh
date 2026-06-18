output=$1
process=""
#process=NanoAODv15
years=(2022__ 2022EE__ 2023__ 2023BPix__ 2024__ )
if [[ $output == "skim" ]]; then
    input_file=skim_args.txt
    amend_file=amend_skim_args.txt
    > $amend_file
    output_dir=/store/user/xinlong/TTAnomalous/quick_selection
    output_files=$(eosls $output_dir/*$process*)
    declare -A classified_files
    for file in ${output_files[@]}; do
        for year in ${years[@]}; do
            if [[ $file == *"output.log"* ]]; then
                continue
            fi
            if [[ $file == *"$year"* ]]; then
                classified_files["$year"]="${classified_files["$year"]} $file"        
                break
            fi
        done
    done
    while IFS= read -r line; do
        if [[ $line != *$process* ]]; then
            continue
        fi
        #echo "$line"
        input_arg=$(echo "$line" | awk '{print $2}')
        file_base=$(basename $input_arg)
        file_base="${file_base%.*}"
        input_y=$(echo "$line" | awk '{print $4}')__
        input_n=$(echo "$line" | awk '{print $6}')
        input_i=$(echo "$line" | awk '{print $8}')
        n_base="n-"$input_n
        i_base="i-"$input_i
        found=0
        for file in ${classified_files["$input_y"]}; do
            #echo $file
            if [[ $file == *"$file_base"* && $file == *"$n_base"* && $file == *"$i_base"* ]]; then
                found=1
                classified_files["$input_y"]="${classified_files[$input_y]//$file/}"
                break
            fi
        done
        if [[ $found == 0 ]] ; then
            echo Missing $line
            echo $line >> $amend_file
        fi
            
    done < $input_file

elif [[ $output == "direct_selection" ]]; then
    input_file=direct_selection_args.txt
    amend_file=amend_direct_selection_args.txt
    > $amend_file
    output_dir=/store/user/xinlong/XHY4bRun3_direct_selection
    output_files=$(eosls $output_dir/*$process*)
    declare -A classified_files
    for file in ${output_files[@]}; do
        for year in ${years[@]}; do
            if [[ $file == *"output.log"* ]]; then
                continue
            fi
            if [[ $file == *"$year"* ]]; then
                classified_files["$year"]="${classified_files["$year"]} $file"        
                break
            fi
        done
    done
    while IFS= read -r line; do
        if [[ $line != *$process* ]]; then
            continue
        fi
        #echo "$line"
        input_arg=$(echo "$line" | awk '{print $2}')
        file_base=$(basename $input_arg)
        file_base="${file_base%.*}"
        input_y=$(echo "$line" | awk '{print $4}')__
        input_n=$(echo "$line" | awk '{print $6}')
        input_i=$(echo "$line" | awk '{print $8}')
        n_base="n-"$input_n
        i_base="i-"$input_i
        found=0
        for file in ${classified_files["$input_y"]}; do
            if [[ $file == *"$file_base"* && $file == *"$n_base"* && $file == *"$i_base"* ]]; then
                found=1
                classified_files["$input_y"]="${classified_files[$input_y]//$file/}"
                break
            fi
        done
        if [[ $found == 0 ]] ; then
            echo Missing $line
            echo $line >> $amend_file
        fi
            
    done < $input_file

elif [[ $output == "selection_"*"_BDT" ]]; then
    echo $output
    amend_file=amend_selection_args.txt
    > $amend_file
    input_file=selection_args.txt
    output_dir=/store/user/xinlong/XHY4bRun3_$output
    output_files=$(eosls $output_dir/*$process*)
    declare -A classified_files
    for file in ${output_files[@]}; do
        for year in ${years[@]}; do
            if [[ $file == *"Template"* || $file == *"RegSig"* ]]; then
                continue
            fi
            if [[ $file == *"$year"* ]]; then
                classified_files["$year"]="${classified_files["$year"]} $file"        
                break
            fi
        done
    done
    #echo ${classified_files["2024__"]}
    while IFS= read -r line; do
        #echo $line
        if [[ $line != *$process* ]]; then
            continue
        fi
        input_arg=$(echo "$line" | awk '{print $2}')
        file_base=$(basename $input_arg)
        file_base="${file_base%.*}"
        input_y=$(echo "$line" | awk '{print $4}')__
        input_n=$(echo "$line" | awk '{print $6}')
        input_i=$(echo "$line" | awk '{print $8}')
        JME_base=$(echo "$line" | awk '{print $10}')
        n_base="n-"$input_n
        i_base="i-"$input_i
        found=0
        for file in ${classified_files["$input_y"]}; do
            #echo $file
            if [[ $file != *"Templates"* && $file == *"$file_base"* && $file == *"$n_base"* && $file == *"$i_base"* && $file == *"$JME_base"* ]]; then
                #echo $file
                found=1
                #classified_files["$input_y"]="${classified_files[$input_y]//$file/}"
                break
            fi
        done
        if [[ $JME_base == "nom"  && $found == 0 ]]; then
            found=0
            for file in ${classified_files["$input_y"]}; do
                
                if [[ $file == *"Templates"* && $file == *"$file_base"* && $file == *"$n_base"* && $file == *"$i_base"* && $file == *"$JME_base"* ]]; then                
                    found=1
                    echo TEST
                    classified_files["$input_y"]="${classified_files[$input_y]//$file/}"
                    #echo $file
                    break
                fi
            done
        fi

        if [[ $found == 0 ]] ; then
            echo $file_base $n_base $i_base $JME_base
            echo Missing $line
            echo $line >> $amend_file
        fi
            
    done < $input_file

elif [[ $output == "Nminus1_1p1" ]]; then
    input_file=selection_args.txt
    output_dir=/store/user/xinlong/XHY4bRun3_Nminus1_1p1
    output_files=$(eosls $output_dir)
    while IFS= read -r line; do
        #echo "$line"
        input_arg=$(echo "$line" | awk '{print $2}')
        file_base=$(basename $input_arg)
        file_base="${file_base%.*}"
        input_n=$(echo "$line" | awk '{print $6}')
        input_i=$(echo "$line" | awk '{print $8}')
        JME_base=$(echo "$line" | awk '{print $10}')
        if [[ $file_base != *"MC"* || $JME_base != "nom" ]]; then
            continue
        fi
        n_base="n-"$input_n
        i_base="i-"$input_i
        found=0
        for file in ${output_files[@]}; do
            if [[ $file != *"Templates"* && $file == *"$file_base"* && $file == *"$n_base"* && $file == *"$i_base"* && $file == *"$JME_base"* ]]; then
                #echo $file
                found=1
                break
            fi
        done
        if [[ $JME_base == "nom"  && $found == 1 ]]; then
            found=0
            for file in ${output_files[@]}; do
                if [[ $file == *"Templates"* && $file == *"$file_base"* && $file == *"$n_base"* && $file == *"$i_base"* && $file == *"$JME_base"* ]]; then                
                    found=1
                    #echo $file
                    break
                fi
            done
        fi

        if [[ $found == 0 ]] ; then
            echo $file_base $n_base $i_base $JME_base
            echo Missing $line
        fi
            
    done < $input_file


elif [[ $output == "division_1p1" ]]; then
    amend_file=amend_division_args.txt
    > $amend_file
    output_dir=/store/user/xinlong/XHY4bRun3_skim
    input_file=division_args.txt
    output_dir=/store/user/xinlong/XHY4bRun3_division_1p1
    output_files=$(eosls $output_dir)
    declare -A classified_files
    for file in ${output_files[@]}; do
        for year in ${years[@]}; do
            if [[ $file == *"output.log"* ]]; then
                continue
            fi
            if [[ $file == *"$year"* ]]; then
                classified_files["$year"]="${classified_files["$year"]} $file"        
                break
            fi
        done
    done
    while IFS= read -r line; do
        #echo "$line"
        input_arg=$(echo "$line" | awk '{print $2}')
        file_base=$(basename $input_arg)
        file_base="${file_base%.*}"
        input_y=$(echo "$line" | awk '{print $4}')__
        input_n=$(echo "$line" | awk '{print $6}')
        input_i=$(echo "$line" | awk '{print $8}')
        n_base="n-"$input_n
        i_base="i-"$input_i
        found_all=1
        regions=(SR1 SR2 SB1 SB2 VB1 VB2 VS1 VS2 VS3 VS4)
        for region in ${regions[@]}; do
            found=0
            for file in ${classified_files["$input_y"]}; do
                if [[ $file != *"Templates"* && $file == *"$file_base"* && $file == *"$n_base"* && $file == *"$i_base"* && $file == *"$region"* ]]; then
                    #echo $file
                    #classified_files["$input_y"]="${classified_files[$input_y]//$file/}"
                    found=1
                    break
                fi
            done
            if [[ $found == 1 ]]; then
                found=0
                for file in ${output_files[@]}; do
                    if [[ $file == *"Templates"* && $file == *"$file_base"* && $file == *"$n_base"* && $file == *"$i_base"* && $file == *"$region_base"* ]]; then                
                        found=1
                        #classified_files["$input_y"]="${classified_files[$input_y]//$file/}"
                        #echo $file
                        break
                    fi
                done
            fi

            if [[ $found == 0 ]] ; then
                found_all=0
                break
                #echo $file_base $n_base $i_base $region
                #echo Missing $line in region $region
                #echo $line >> $amend_file 
            fi
        done
        if [[ $found_all == 0 ]] ; then
                echo Missing $line
                echo $line >> $amend_file 
        fi
            
    done < $input_file
fi
