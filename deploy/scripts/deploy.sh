#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   deploy/scripts/deploy.sh <function-name> <role-arn> [region]
# Requires AWS CLI configured.

FN=${1:-reddit-probe}
ROLE=${2:-}
REGION=${3:-}

if [[ -z "$ROLE" ]]; then
  echo "Usage: $0 <function-name> <role-arn> [region]" >&2
  exit 2
fi

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
ZIP_PATH="$ROOT_DIR/build/package.zip"

if [[ ! -f "$ZIP_PATH" ]]; then
  echo "package.zip not found. Run deploy/scripts/build_and_zip.sh first." >&2
  exit 2
fi

AWS=(aws)
[[ -n "$REGION" ]] && AWS+=(--region "$REGION")

set +e
${AWS[@]} lambda get-function --function-name "$FN" >/dev/null 2>&1
EXISTS=$?
set -e

if [[ $EXISTS -ne 0 ]]; then
  echo "[deploy] creating function $FN"
  ${AWS[@]} lambda create-function \
    --function-name "$FN" \
    --runtime python3.12 \
    --handler handler.lambda_handler \
    --zip-file fileb://"$ZIP_PATH" \
    --role "$ROLE" \
    --architecture arm64 \
    --timeout 900 \
    --memory-size 1024 \
    --environment "Variables={LOG_LEVEL=INFO}"
else
  echo "[deploy] updating code for $FN"
  ${AWS[@]} lambda update-function-code \
    --function-name "$FN" \
    --zip-file fileb://"$ZIP_PATH"
fi

echo "[deploy] done"


