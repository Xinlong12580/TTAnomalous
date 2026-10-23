#!/usr/bin/env bash
set -euo pipefail
signal=$1
year=$2
PostFitShapesFromWorkspace  -w higgsCombineSnapshot.MultiDimFit.mH125.root --output shapes_clean.root -d card.txt -f multidimfitSnapshot.root:fit_mdf --postfit  
python plot_workspace.py --sig $signal --year $year
