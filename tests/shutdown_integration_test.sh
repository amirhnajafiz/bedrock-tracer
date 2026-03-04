#!/usr/bin/env sh

set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
OUT_DIR="${TMPDIR:-/tmp}/bdtrace-shutdown-it-$$"
RUNNER_PID=""

cleanup() {
    if [ -n "${RUNNER_PID}" ] && kill -0 "${RUNNER_PID}" 2>/dev/null; then
        kill -KILL "${RUNNER_PID}" 2>/dev/null || true
    fi

    rm -rf "${OUT_DIR}" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

if [ "$(id -u)" -ne 0 ]; then
    echo "[FAIL] shutdown integration test requires root privileges."
    echo "Run with: sudo sh tests/shutdown_integration_test.sh"
    exit 1
fi

if ! command -v bdtrace >/dev/null 2>&1; then
    echo "[FAIL] bdtrace command not found in PATH."
    exit 1
fi

mkdir -p "${OUT_DIR}"

SCRIPT_ROOT="${ROOT_DIR}/bpftrace/"

find_matching_bpftrace_pids() {
    ps -axo pid=,command= | awk -v pat="${SCRIPT_ROOT}" '
        /bpftrace/ {
            pid = $1
            $1 = ""
            cmd = substr($0, 2)
            if (index(cmd, pat) > 0) {
                print pid
            }
        }
    ' | sort -n
}

baseline_pids="$(find_matching_bpftrace_pids | tr '\n' ' ')"

echo "[INFO] starting bdtrace in background ..."
bdtrace --execute "sleep 120" --out "${OUT_DIR}" --debug >/tmp/bdtrace-shutdown-it.log 2>&1 &
RUNNER_PID="$!"

sleep 3

echo "[INFO] sending SIGTERM to bdtrace (pid=${RUNNER_PID}) ..."
kill -TERM "${RUNNER_PID}" 2>/dev/null || true

wait_steps=0
while kill -0 "${RUNNER_PID}" 2>/dev/null && [ "${wait_steps}" -lt 30 ]; do
    sleep 0.5
    wait_steps=$((wait_steps + 1))
done

if kill -0 "${RUNNER_PID}" 2>/dev/null; then
    echo "[FAIL] bdtrace process did not terminate after SIGTERM."
    exit 1
fi

wait "${RUNNER_PID}" || true
RUNNER_PID=""

leftover_pids=""
check_steps=0
while [ "${check_steps}" -lt 40 ]; do
    current_pids="$(find_matching_bpftrace_pids | tr '\n' ' ')"
    leftover_pids=""

    for pid in ${current_pids}; do
        case " ${baseline_pids} " in
            *" ${pid} "*) ;;
            *) leftover_pids="${leftover_pids} ${pid}" ;;
        esac
    done

    if [ -z "${leftover_pids}" ]; then
        echo "[PASS] no residual bdtrace-owned bpftrace process remained after shutdown."
        exit 0
    fi

    sleep 0.25
    check_steps=$((check_steps + 1))
done

echo "[FAIL] residual bpftrace process(es) found:${leftover_pids}"
for pid in ${leftover_pids}; do
    ps -p "${pid}" -o pid=,ppid=,command= || true
done

echo "[INFO] check /tmp/bdtrace-shutdown-it.log for tracer logs."
exit 1
