#!/usr/bin/env bash
set -euo pipefail
years=("2024")
signals=("MC_TTHJets_Hto2B" "MC_TTHJets_Hto2C" "MC_TTHJets_Hto2G" "MC_TTZJets_ZtoQQ" "MC_TTTT" "MC_TTLL_MLL50" "MC_TTH_TTToAll_HToAATo4B_M30")
for year in ${years[@]}; do
    for signal in ${signals[@]}; do
        cp run_fit.sh workspace_${year}_${signal}
        cd workspace_${year}_${signal}
        ./run_fit.sh
        cd ..
    done
done
