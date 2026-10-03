#!/usr/bin/env bash

set -u

PASSED=0
FAILED=0

run_test() {
    echo
    echo "============================================================"
    echo "RUNNING: $*"
    echo "============================================================"

    if "$@"; then
        echo "OK: $*"
        PASSED=$((PASSED + 1))
    else
        echo "FAIL: $*"
        FAILED=$((FAILED + 1))
    fi
}


run_test python main.py --mutation nrf_disc_auth_slice

run_test python main.py --mutation udm_resynchronization
run_test python main.py --mutation udm_suci_deconcealment

run_test python main.py --mutation amf_sync_failure_case_a --variant static
run_test python main.py --mutation amf_sync_failure_case_a --variant temporal
run_test python main.py --mutation amf_sync_failure_case_a --variant both

run_test python main.py --mutation amf_sync_failure_case_b --variant static
run_test python main.py --mutation amf_sync_failure_case_b --variant temporal
run_test python main.py --mutation amf_sync_failure_case_b --variant both

run_test python main.py --mutation upf_teid_uniqueness --variant fail
run_test python main.py --mutation upf_teid_uniqueness --variant inconclusive

run_test python main.py --mutation resstar_verification_failure --case A
run_test python main.py --mutation resstar_verification_failure --case B
run_test python main.py --mutation resstar_verification_failure --case C
run_test python main.py --mutation resstar_verification_failure --case D


echo
echo "============================================================"
echo "MUTATION REGRESSION SUMMARY"
echo "============================================================"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "Total:  $((PASSED + FAILED))"

if [ "$FAILED" -ne 0 ]; then
    exit 1
fi

exit 0