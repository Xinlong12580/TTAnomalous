#!/usr/bin/env bash
set -euo pipefail
templates=$(ls Templates/*)
for template in $templates; do
    if [[ $template == *"MCstat"* || $template == *"rebinned"* ]]; then
        continue
    fi
    echo $template
    python hist_rebinning.py -f $template --year Allyears --recreate
    python hist_rebinning.py -f $template  --year 2024
done
