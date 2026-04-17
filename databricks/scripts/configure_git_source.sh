#!/usr/bin/env bash

set -euo pipefail

APP_NAME="${APP_NAME:-caltrans-pde-app}"
GIT_REPO_URL="${GIT_REPO_URL:-https://github.com/LLM-AI-INDIA/Caltrans-AI-.git}"
GIT_PROVIDER="${GIT_PROVIDER:-gitHub}"
GIT_BRANCH="${GIT_BRANCH:-main}"
GIT_SOURCE_PATH="${GIT_SOURCE_PATH:-databricks}"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

require_cmd databricks
require_cmd python3

PAYLOAD="$(
  python3 -c 'import json,sys; print(json.dumps({
    "update_mask": "git_repository",
    "git_repository": {
      "provider": sys.argv[1],
      "url": sys.argv[2]
    }
  }))' "${GIT_PROVIDER}" "${GIT_REPO_URL}"
)"

echo "Configuring Git repository for ${APP_NAME}..."
databricks apps create-update "${APP_NAME}" --json "${PAYLOAD}"

echo "Git repository configured."
echo "In the Databricks Apps UI, choose Deploy -> From Git, then use:"
echo "  branch: ${GIT_BRANCH}"
echo "  source code path: ${GIT_SOURCE_PATH}"
