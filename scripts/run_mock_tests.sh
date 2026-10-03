#!/usr/bin/env bash
# ==============================================================================
# Run Mock Server & Network Interception Test Suites
# Default: Headless. Pass --headed to run with a visible browser.
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif [ -f "/opt/miniconda3/envs/playwright-env/bin/python" ]; then
    PYTHON_CMD="/opt/miniconda3/envs/playwright-env/bin/python"
else
    PYTHON_CMD="python"
fi

${PYTHON_CMD} "${SCRIPT_DIR}/run_mock_tests.py" "$@"

