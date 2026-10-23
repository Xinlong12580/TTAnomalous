#!/usr/bin/env bash
set -euo pipefail
card=card.txt
wsm=card.root
(set -x; text2workspace.py $card -o $wsm --verbose 3)

(set -x; combine -D data_obs -M MultiDimFit --saveWorkspace -m 125 -d $wsm -v 1 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1 --X-rtd MINIMIZER_MaxCalls=4000000 --setParameters r=0 -n Snapshot --saveFitResult -t -1)
(set -x; combine -D data_obs -M AsymptoticLimits --saveWorkspace -m 125 -d $wsm -v 1 --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.1 --X-rtd MINIMIZER_MaxCalls=4000000 --setParameters r=0 -n Snapshot  -t -1)

