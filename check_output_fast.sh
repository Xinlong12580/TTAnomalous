#!/usr/bin/env bash

# Fast, exact replacement for `check_output.sh skim`.
#
# The historical "skim" mode checks the muon quick-selection snapshots stored
# in TTAnomalous/quick_selection, rather than the outputs made by run_skim.py.

set -euo pipefail

mode=${1:-}

if [[ "$mode" != "skim" ]]; then
    echo "Usage: $0 skim" >&2
    exit 2
fi

input_file=${INPUT_FILE:-skim_args.txt}
amend_file=${AMEND_FILE:-amend_skim_args.txt}
output_dir=${OUTPUT_DIR:-/store/user/xinlong/TTAnomalous/quick_selection}
output_prefix=${OUTPUT_PREFIX:-Muon_RegSig__1p1_tagged_selected_}
eos_endpoint=${EOS_ENDPOINT:-root://cmseos.fnal.gov}

if [[ ! -r "$input_file" ]]; then
    echo "ERROR: Cannot read input argument file: $input_file" >&2
    exit 2
fi

temp_dir=$(mktemp -d /tmp/check_output_fast.XXXXXX)
output_list="$temp_dir/eos_files.txt"
amend_temp="$temp_dir/amend_args.txt"

cleanup() {
    rm -f -- "$output_list" "$amend_temp"
    rmdir "$temp_dir" 2>/dev/null || true
}
trap cleanup EXIT

# Do not touch the existing amendment file unless the EOS listing succeeds.
if ! eos "$eos_endpoint" ls "$output_dir" > "$output_list"; then
    echo "ERROR: Failed to list $eos_endpoint/$output_dir" >&2
    exit 1
fi

if ! awk \
    -v output_list="$output_list" \
    -v output_prefix="$output_prefix" '
BEGIN {
    actual_count = 0
    expected_count = 0
    missing_count = 0
    unexpected_count = 0

    while ((getline file < output_list) > 0) {
        # Requiring the exact workflow prefix excludes Templates_Muon_* and
        # products from electron, generic, or control-region workflows.
        if (index(file, output_prefix) == 1) {
            actual[file] = 1
            actual_count++
        }
    }
    close(output_list)
}

/^[[:space:]]*$/ || /^[[:space:]]*#/ {
    next
}

{
    if (NF != 8 || $1 != "-d" || $3 != "-y" ||
        $5 != "-n" || $7 != "-i") {
        print "ERROR: Malformed argument line " NR ": " $0 > "/dev/stderr"
        malformed = 1
        next
    }

    base = $2
    sub(/^.*\//, "", base)
    sub(/\.txt$/, "", base)

    expected_file = output_prefix base "_n-" $6 "_i-" $8 ".root"
    expected[expected_file] = 1
    expected_count++

    if (!(expected_file in actual)) {
        print $0
        missing_count++
    }
}

END {
    for (file in actual) {
        if (!(file in expected)) {
            unexpected_count++
        }
    }

    print "Expected jobs: " expected_count > "/dev/stderr"
    print "Matching snapshots: " (expected_count - missing_count) > "/dev/stderr"
    print "Missing snapshots: " missing_count > "/dev/stderr"
    print "Unexpected snapshots: " unexpected_count > "/dev/stderr"

    if (malformed) {
        exit 2
    }
}
' "$input_file" > "$amend_temp"; then
    echo "ERROR: Comparison failed; $amend_file was not changed" >&2
    exit 1
fi

mv -- "$amend_temp" "$amend_file"
echo "Missing arguments written to: $amend_file"
