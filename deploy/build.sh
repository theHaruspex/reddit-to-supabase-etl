#!/usr/bin/env bash
# Build a Lambda zip with deps at the zip root using Amazon Linux (Docker by default).
# Env overrides:
#   PY_VERSION (default 3.12)
#   SRC_DIR (default src)
#   REQ_FILE (default requirements.txt)
#   OUT_DIR (default dist)
#   STAGE_DIR (default build/stage)
#   ZIP_NAME (default function_package.zip)
#   LAMBDA_ARCH (x86_64|arm64, default x86_64)
#   USE_DOCKER (1|0, default 1)
set -euo pipefail

# Detect repo root
if ROOT=$(git rev-parse --show-toplevel 2>/dev/null); then
  cd "$ROOT"
else
  cd "$(dirname "$0")/.." # deploy/ → repo root fallback
fi

PY_VERSION=${PY_VERSION:-"3.12"}
SRC_DIR=${SRC_DIR:-"src"}
REQ_FILE=${REQ_FILE:-"requirements.txt"}
OUT_DIR=${OUT_DIR:-"dist"}
STAGE_DIR=${STAGE_DIR:-"build/stage"}
ZIP_NAME=${ZIP_NAME:-"function_package.zip"}
LAMBDA_ARCH=${LAMBDA_ARCH:-"x86_64"}
USE_DOCKER=${USE_DOCKER:-"1"}

if [[ "$LAMBDA_ARCH" == "arm64" ]]; then
  DOCKER_PLATFORM="linux/arm64"
else
  DOCKER_PLATFORM="linux/amd64"
fi

cleanup() {
  rm -rf "$STAGE_DIR" "$OUT_DIR"
  mkdir -p "$STAGE_DIR" "$OUT_DIR"
}

verify_imports_py='import sys, platform; mods=["pydantic_core","pydantic"];\
for m in mods:\n\
    try:\n\
        __import__(m); print(f"verify: imported {m}")\n\
    except Exception as e:\n\
        print(f"verify: FAILED importing {m}: {e!r}"); raise\n\
print("verify: platform:", platform.platform()); print("verify: python:", sys.version)'

build_host() {
  echo "==> Host build (Linux host assumed)"
  cleanup
  python${PY_VERSION} -m pip install --upgrade pip
  if [[ -f "$REQ_FILE" ]]; then
    python${PY_VERSION} -m pip install -r "$REQ_FILE" -t "$STAGE_DIR"
  fi
  rsync -a --exclude '__pycache__' --exclude '.DS_Store' "$SRC_DIR/" "$STAGE_DIR/"
  [[ -f "$STAGE_DIR/handler.py" ]] || { echo "ERROR: $SRC_DIR/handler.py missing"; exit 1; }
  (cd "$STAGE_DIR" && python -c "$verify_imports_py")
  (cd "$STAGE_DIR" && zip -X -r "../../$OUT_DIR/$ZIP_NAME" .)
  echo "==> Built $OUT_DIR/$ZIP_NAME"
}

build_docker() {
  echo "==> Docker build on $DOCKER_PLATFORM using public.ecr.aws/lambda/python:${PY_VERSION}"
  cleanup
  docker run --rm -t \
    -v "$(pwd)":/pkg -w /pkg \
    --platform "$DOCKER_PLATFORM" \
    public.ecr.aws/lambda/python:${PY_VERSION} \
    bash -lc "set -euo pipefail; \
      python -m pip install --upgrade pip; \
      if [ -f '$REQ_FILE' ]; then pip install -r '$REQ_FILE' -t '$STAGE_DIR'; fi; \
      rsync -a --exclude '__pycache__' --exclude '.DS_Store' '$SRC_DIR'/ '$STAGE_DIR'/; \
      [ -f '$STAGE_DIR/handler.py' ] || { echo 'ERROR: $SRC_DIR/handler.py missing'; exit 1; }; \
      (cd '$STAGE_DIR' && python -c "$verify_imports_py"); \
      (cd '$STAGE_DIR' && zip -X -r '../..'/'$OUT_DIR'/'$ZIP_NAME' .)"
  echo "==> Built $OUT_DIR/$ZIP_NAME"
}

if [[ "$USE_DOCKER" == "1" ]]; then
  build_docker
else
  build_host
fi

echo "\nNext: aws lambda update-function-code --function-name <name> --zip-file fileb://$OUT_DIR/$ZIP_NAME"

