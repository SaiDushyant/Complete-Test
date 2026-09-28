#!/usr/bin/env bash
# ==============================================================================
# Run Trade Terminal Behavioral Workflow Tests (Developer 1)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

echo "=================================================="
echo "🚀 Running Trade Terminal Workflow Test Suite"
echo "=================================================="

# Check if pytest is directly available or in playwright-env
if command -v pytest >/dev/null 2>&1; then
    PYTEST_CMD="pytest"
elif [ -f "/opt/miniconda3/envs/playwright-env/bin/pytest" ]; then
    PYTEST_CMD="/opt/miniconda3/envs/playwright-env/bin/pytest"
else
    PYTEST_CMD="python -m pytest"
fi

if [ $# -eq 0 ]; then
    ${PYTEST_CMD} workflows/trade_terminal/tests
else
    HAS_PATH=false
    for arg in "$@"; do
        if [[ ! "$arg" =~ ^- ]]; then
            HAS_PATH=true
            break
        fi
    done
    if [ "$HAS_PATH" = true ]; then
        ${PYTEST_CMD} "$@"
    else
        ${PYTEST_CMD} workflows/trade_terminal/tests "$@"
    fi
fi
