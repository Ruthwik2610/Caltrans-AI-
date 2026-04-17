#!/usr/bin/env bash

set -euo pipefail

APP_NAME="${APP_NAME:-caltrans-pde-app}"
BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-/Workspace/Shared/apps/${APP_NAME}/default}"
SOURCE_PATH="${SOURCE_PATH:-${WORKSPACE_ROOT}/files}"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

require_cmd databricks
require_cmd python3

cd "${BUNDLE_DIR}"

echo "Validating Databricks bundle..."
databricks bundle validate

echo "Ensuring shared workspace folders exist..."
databricks workspace mkdirs "${WORKSPACE_ROOT}"
databricks workspace mkdirs "${SOURCE_PATH}"

APP_JSON="$(databricks apps get "${APP_NAME}" -o json)"
SP_CLIENT_ID="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["service_principal_client_id"])' <<<"${APP_JSON}")"

TARGET_STATUS="$(databricks workspace get-status "${WORKSPACE_ROOT}" -o json)"
TARGET_ID="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["object_id"])' <<<"${TARGET_STATUS}")"

echo "Granting the app service principal read access to ${WORKSPACE_ROOT}..."
databricks workspace update-permissions directories "${TARGET_ID}" --json "$(
  python3 -c 'import json,sys; print(json.dumps({
    "access_control_list": [
      {
        "service_principal_name": sys.argv[1],
        "permission_level": "CAN_READ"
      }
    ]
  }))' "${SP_CLIENT_ID}"
)"

echo "Binding bundle resource to the existing Databricks app..."
BIND_LOG="$(mktemp)"
if ! databricks bundle deployment bind caltrans_pde_app "${APP_NAME}" --auto-approve >"${BIND_LOG}" 2>&1; then
  if grep -q "Resource already managed by Terraform" "${BIND_LOG}"; then
    echo "Bundle resource already bound. Continuing with deployment."
  else
    cat "${BIND_LOG}" >&2
    rm -f "${BIND_LOG}"
    exit 1
  fi
fi
rm -f "${BIND_LOG}"

echo "Deploying app from workspace source..."
databricks bundle deploy

echo "Verifying uploaded source files..."
databricks workspace list "${SOURCE_PATH}"
