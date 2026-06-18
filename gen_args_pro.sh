operation=$1
input=$2
output="$operation"_args.txt
> $output
if [[ $operation == "skim" || $operation == *"direct_selection"* ]] ; then
    files=raw_nano/files/*.txt
    #files=raw_nano/files_original_dataset/*.txt
    n_files_base=1
else
    files=outputList/"${input^^}"*.txt
    n_files_base=10000
fi
debug=0
if [[ $operation == *"debug"* ]] ; then
    debug=1
fi
debug=0
for file in $files; do
    if [[ ( $operation == *"selection"* || $operation == *"Nminus1"* ) && ( $file == *"QCD"* ||  $file == *"Data"* ) ]] ; then
        n_files=3
    elif [[ ( $operation == *"selection"* || $operation == *"Nminus1"* ) && ( $file == *"TTBar"* || $file == *"WZ"* ) ]] ; then
        n_files=3
    else
        n_files=$n_files_base
    fi
    if [[ $operation == *"direct_selection"* && $file == *"QCD"* && $file != *2024* ]]; then
        n_files=10
    fi
    if [[  ( $operation == *"skim"* ) && ( $file != *"24"* ) && ( $file == *"QCD"* || $file == *"Signal"* ) ]] ; then
        n_files=10
    fi 
        
    pass=0
    #if [[ "$file" == *"SignalMC"* ]]; then
    #    pass=1
    #elif [[ "$file" == *"MX-3000_MY-300"* ]]; then
    #    pass=1
    #fi
    if [[  $operation == *"Nminus1"* && "$file" == *"Data"* ]]; then
        pass=0
    fi 
    if [[ $file != *"2022EE"*"Signal"* ]]; then
        pass=0
    fi
    if [[ $file == *"Signal"* || $file == *"TTBar"* || $file == *"QCD"* || $file == *"Data"* ]]; then
        pass=1
    fi
    if [[ $debug == 0 ]]; then
        pass=0
        
        #if [[ ( $file == *"QCD"* || $file == *"JetMET"* ) && $file != *"2022EE"* ]]; then
        if [[ ( $file == *"JetMET"* || $file == *"TTBar"* || $file == *"Signal"* ) ]]; then
            pass=1
        fi
    fi
    pass=0
    if [[  ($file == *"TTBar"* || $file == *"Data"* || $file == *"SignalMC"* ) && $file != *"2024"*  ]]; then
    #if [[  ($file == *"TTBar"* || $file == *"Data"*  ) && $file != *"2024"*  ]]; then
        pass=0
    fi
    if [[  ( $file == *"QCD"* )  ]]; then
        pass=0
    fi
    #if [[  (  $file == *"2024"*"JetMET"* )  ]]; then
    #if [[  (  $file == *"TTBar"* || $file == *"QCD"* || $file == *"Signal"* ) ]]; then
    #if [[  ( $file != *"2022_"* && $file != *"2024_"* && $file == *"QCD"* ) ]]; then
    #if [[  ( $file == *"TTto4Q"* || $file == *"Data"*   ) ]]; then
    #if [[  (  $file == *"Data"* || $file == *"Signal"* || $file == *"TTBar"*  ) ]]; then
    #if [[  (  $file != *"QCD"* && $file == *"2024"*  ) ]]; then
    if [[  (  ( $file == *"QCD"* || $file == *"JetMET"* ) && $file == *"2024"*  ) ]]; then
    #if [[  (  $file == *"QCD"* && $file != *"HT-100to"*   ) ]]; then
        pass=1
    fi
    debug=1
    if [[ $operation == *"selection"* && $pass == 1 ]]; then
        Regs=("-r Signal" "-r Control" "-r Validation")
        #Regs=("-r Signal")
        #Regs=("-r Control")
        #Regs=("-r AValidation")
        JMEs=("-s nom" "-s JES__up" "-s JES__down" "-s JER__up" "-s JER__down")
        JMEs=("-s nom")
        if [[ $debug == 1 ]]; then
            JMEs=("-s nom")
        fi
        extras=()
        for Reg in "${Regs[@]}"; do
            for JME in "${JMEs[@]}"; do
                extras+=("$JME $Reg")
            done
        done
        for extra in "${extras[@]}"; do
            echo $extra
            if [[ $pass == 1 ]] ; then
                if [[ "$file" == *"2022__"* ]]; then
                    ./gen_args.sh $file 2022 $output $n_files "$extra"
                elif [[ "$file" == *"2022EE__"* ]]; then
                    ./gen_args.sh $file 2022EE $output $n_files "$extra"
                elif [[ "$file" == *"2023__"* ]]; then
                    ./gen_args.sh $file 2023 $output $n_files "$extra"
                elif [[ "$file" == *"2023BPix__"* ]]; then
                    ./gen_args.sh $file 2023BPix $output $n_files "$extra"
                elif [[ "$file" == *"2024"* ]]; then
                    ./gen_args.sh $file 2024 $output $n_files "$extra"
                fi
            fi
            #if [[ $file == *"Data"* || $file == *"QCD"* || $file == *"DiBoson"* || $file == *"SingleTop"* || $file == *"Higgs"* ]]; then
            #    break
            #fi
        done
    else
        if [[ $pass == 1 ]]; then
            if [[ "$file" == *"2022__"* ]]; then
                ./gen_args.sh $file 2022 $output $n_files
            elif [[ "$file" == *"2022EE__"* ]]; then
                ./gen_args.sh $file 2022EE $output $n_files
            elif [[ "$file" == *"2023__"* ]]; then
                ./gen_args.sh $file 2023 $output $n_files
            elif [[ "$file" == *"2023BPix__"* ]]; then
                ./gen_args.sh $file 2023BPix $output $n_files
            elif [[ "$file" == *"2024__"* ]]; then
                ./gen_args.sh $file 2024 $output $n_files
            fi
        fi
    fi
    
done
