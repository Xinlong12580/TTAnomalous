work=$1
if [[ $work == skim ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_skim.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/TTAnomalous/skim/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a skim_args.txt -i "run_skim.py TTAnomalous_Analyzer.py raw_nano cpp_modules outputList"
fi

if [[ $work == quick_selection ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_quick_selection.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/TTAnomalous/quick_selection/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a skim_args.txt -i "run_quick_selection.py TTAnomalous_Analyzer.py raw_nano cpp_modules outputList"
fi

if [[ $work == quick_selection_control ]] ; then
    sed -e 's/PYTHON_SCRIPT/run_quick_selection_control.py/g' -e 's#OUTPUT_DIR#root://cmseos.fnal.gov//store/user/USER_NAME/TTAnomalous/quick_selection/#g' -e "s/USER_NAME/$USER/g" gridrun_template.sh > gridrun.sh
    python CondorHelper.py -r gridrun.sh -a skim_args.txt -i "run_quick_selection_control.py TTAnomalous_Analyzer.py raw_nano cpp_modules outputList"
fi

