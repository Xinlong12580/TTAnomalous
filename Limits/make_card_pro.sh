#!/usr/bin/env bash
set -euo pipefail
years=("2024")
signals=("MC_TTHJets_Hto2B" "MC_TTHJets_Hto2C" "MC_TTHJets_Hto2G" "MC_TTZJets_ZtoQQ" "MC_TTTT" "MC_TTLL_MLL50" "MC_TTH_TTToAll_HToAATo4B_M30")
for year in ${years[@]}; do
    for signal in ${signals[@]}; do
        mkdir workspace_${year}_${signal}
        python make_card.py --sig $signal  --year $year --input_file '../Templates/Templates_Signal_all_rebinned.root'
        mv card.txt workspace_${year}_${signal}
    done
done
