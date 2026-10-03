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


run_test python main.py --test nrf_disc_auth_slice
run_test python main.py --test udm_resynchronization
run_test python main.py --test udm_suci_deconcealment

run_test python main.py --test amf_sync_failure_case_a
run_test python main.py --test amf_sync_failure_case_b

run_test python main.py --test upf_teid_uniqueness

run_test python main.py --test resstar_verification_failure --case A
run_test python main.py --test resstar_verification_failure --case B
run_test python main.py --test resstar_verification_failure --case C
run_test python main.py --test resstar_verification_failure --case D


echo
echo "============================================================"
echo "BASELINE REGRESSION SUMMARY"
echo "============================================================"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "Total:  $((PASSED + FAILED))"

if [ "$FAILED" -ne 0 ]; then
    exit 1
fi

exit 0