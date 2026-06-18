xroot_fs=$( ls files_xrootd)
for xroot_f in $xroot_fs; do
    if [[ $xroot_f != *"Data"* && $xroot_f != *"2024"* && $xroot_f != *"TTBar"* ]]; then
        echo converting $xroot_f
        sed 's|cmsxrootd|cmseos|g' files_xrootd/$xroot_f > files/$xroot_f
        grep -v "25v1" files/$xroot_f > files/tmp_$xroot_f && mv files/tmp_$xroot_f files/$xroot_f
    else
        echo cping $xroot_f
        #sed 's|cmsxrootd.fnal.gov|cms-xrd-global.cern.ch|g' files_xrootd/$xroot_f > files/$xroot_f
        sed 's|cmsxrootd.fnal.gov|cmsxrootd.fnal.gov|g' files_xrootd/$xroot_f > files/$xroot_f
        #cp files_xrootd/$xroot_f files/$xroot_f
        grep -v "25v1" files/$xroot_f > files/tmp_$xroot_f && mv files/tmp_$xroot_f files/$xroot_f
    fi 
done
