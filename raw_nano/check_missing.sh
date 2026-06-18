files0=$( ls btagging_effs/202* )
files1=$( ls Xbbtagging_effs/2p1* )

for f in $files0; do
    tmp="${f#*effs/}"
    dataset="${tmp%%_AK*}"
    #echo $dataset
    found=0
    for f1 in $files1; do
        if [[ $f1 = *"$dataset"* ]]; then
            found=1
            break
        fi
    done
    if [[ $found == 0 ]]; then
        echo missing $dataset
    fi
done
