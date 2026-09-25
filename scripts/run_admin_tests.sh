#!/usr/bin/env bash
# ==============================================================================
# Run Admin Portal Behavioral Workflow Tests (Developer 2)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

echo "=================================================="
echo "🚀 Running Admin Portal Workflow Test Suite"
echo "=================================================="

if command -v pytest >/dev/null 2>&1; then
    PYTEST_CMD="pytest"
elif [ -f "/opt/miniconda3/envs/playwright-env/bin/pytest" ]; then
    PYTEST_CMD="/opt/miniconda3/envs/playwright-env/bin/pytest"
else
    PYTEST_CMD="python -m pytest"
fi

${PYTEST_CMD} workflows/admin_portal/tests "$@"
