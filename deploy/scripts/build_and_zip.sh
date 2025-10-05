#!/usr/bin/env bash
set -euo pipefail

# Build a Lambda zip with deps at the root (no python/), compatible with Lambda.
# Defaults can be overridden via env: USE_DOCKER, PY_VERSION, LAMBDA_ARCH, SRC_DIR, REQ_FILE, BUILD_DIR, OUT_DIR, ZIP_NAME

# Detect repo root (prefer git), fallback relative to this script
if ROOT_DIR=$(git rev-parse --show-toplevel 2>/dev/null); then :; else ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd); fi
cd "$ROOT_DIR"

PY_VERSION=${PY_VERSION:-"3.12"}
SRC_DIR=${SRC_DIR:-"src"}
REQ_FILE=${REQ_FILE:-"requirements.txt"}
BUILD_DIR=${BUILD_DIR:-"$ROOT_DIR/build"}
STAGE_DIR=${STAGE_DIR:-"$BUILD_DIR/src"}
OUT_DIR=${OUT_DIR:-"$ROOT_DIR/build"}
ZIP_NAME=${ZIP_NAME:-"package.zip"}
ZIP_PATH="$OUT_DIR/$ZIP_NAME"
USE_DOCKER=${USE_DOCKER:-"1"}
LAMBDA_ARCH=${LAMBDA_ARCH:-"x86_64"} # or arm64
DOCKER_PLATFORM=$([ "$LAMBDA_ARCH" = "arm64" ] && echo linux/arm64 || echo linux/amd64)

# Normalize to absolute paths for mapping into container
ABS_SRC_DIR="$SRC_DIR"; [[ "$ABS_SRC_DIR" = /* ]] || ABS_SRC_DIR="$ROOT_DIR/$SRC_DIR"
ABS_OUT_DIR="$OUT_DIR"; [[ "$ABS_OUT_DIR" = /* ]] || ABS_OUT_DIR="$ROOT_DIR/$OUT_DIR"
ABS_STAGE_DIR="$STAGE_DIR"; [[ "$ABS_STAGE_DIR" = /* ]] || ABS_STAGE_DIR="$ROOT_DIR/$STAGE_DIR"

# Container-visible paths (repo mounted at /pkg)
C_SRC_DIR="/pkg${ABS_SRC_DIR#$ROOT_DIR}"
C_OUT_DIR="/pkg${ABS_OUT_DIR#$ROOT_DIR}"
C_STAGE_DIR="/pkg${ABS_STAGE_DIR#$ROOT_DIR}"
C_ZIP_PATH="$C_OUT_DIR/$ZIP_NAME"

echo "[build] cleaning $BUILD_DIR"
rm -rf "$BUILD_DIR" && mkdir -p "$STAGE_DIR" "$OUT_DIR"

echo "[build] preparing requirements.txt"
if [[ -f "$REQ_FILE" ]]; then
  cp "$REQ_FILE" "$STAGE_DIR/requirements.txt"
else
  python - <<'PY'
from pathlib import Path
py = Path('pyproject.toml').read_text()
start = py.find('dependencies = [')
end = py.find(']', start)
deps = []
if start != -1 and end != -1:
    block = py[start:end+1]
    for line in block.split('\n'):
        line=line.strip().strip('",')
        if line and not line.startswith('dependencies') and line not in ('[', ']'):
            deps.append(line)
out = Path('build/src/requirements.txt')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text('\n'.join(deps) + '\n')
print('[build] wrote', out)
PY
fi

# write a small verifier script into the stage directory (simplifies quoting)
cat > "$STAGE_DIR/_verify.py" <<'PY'
import sys, platform
mods = ["pydantic_core", "pydantic", "cffi"]
for m in mods:
    try:
        __import__(m)
        print(f"verify: imported {m}")
    except Exception as e:
        print(f"verify: FAILED importing {m}: {e!r}")
        raise
print("verify: platform", platform.platform())
print("verify: python", sys.version)
PY

# write a small zipper script to avoid relying on external zip util
cat > "$STAGE_DIR/_zip_stage.py" <<'PY'
import os, zipfile
zip_path = os.environ.get('ZIP_PATH')
if not zip_path:
    raise SystemExit('ZIP_PATH env var is required')
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, _, files in os.walk('.'):
        for f in files:
            p = os.path.join(root, f)
            zf.write(p, arcname=os.path.normpath(p))
print('wrote', zip_path)
PY

if [[ "$USE_DOCKER" == "1" ]]; then
  echo "[build] Docker build (platform=$DOCKER_PLATFORM, image=public.ecr.aws/lambda/python:$PY_VERSION)"
  docker run --rm -t \
    -v "$ROOT_DIR":/pkg -w /pkg \
    --platform "$DOCKER_PLATFORM" \
    -e SRC_DIR="$C_SRC_DIR" -e STAGE_DIR="$C_STAGE_DIR" -e ZIP_PATH="$C_ZIP_PATH" \
    --entrypoint bash \
    public.ecr.aws/lambda/python:${PY_VERSION} \
    -lc 'set -euo pipefail; \
      python -m pip install --upgrade pip; \
      if [ -f "$STAGE_DIR/requirements.txt" ]; then pip install -r "$STAGE_DIR/requirements.txt" -t "$STAGE_DIR"; fi; \
      mkdir -p "$STAGE_DIR" && cp -a "$SRC_DIR"/. "$STAGE_DIR"/; \
      cp "/pkg/deploy/lambda/handler.py" "$STAGE_DIR/handler.py"; \
      if [ -f "/pkg/config.yaml" ]; then cp "/pkg/config.yaml" "$STAGE_DIR/config.yaml"; fi; \
      [ -f "$STAGE_DIR/handler.py" ] || { echo "ERROR: handler.py missing after copy"; exit 1; }; \
      (cd "$STAGE_DIR" && python _verify.py && ZIP_PATH="$ZIP_PATH" python _zip_stage.py)'
else
  echo "[build] Host build (ensure Linux for native wheels)"
  python${PY_VERSION} -m pip install --upgrade pip
  if [[ -f "$STAGE_DIR/requirements.txt" ]]; then
    python${PY_VERSION} -m pip install -r "$STAGE_DIR/requirements.txt" -t "$STAGE_DIR"
  fi
  mkdir -p "$STAGE_DIR" && cp -a "$SRC_DIR"/. "$STAGE_DIR"/
  cp "$ROOT_DIR/deploy/lambda/handler.py" "$STAGE_DIR/handler.py"
  if [[ -f "$ROOT_DIR/config.yaml" ]]; then cp "$ROOT_DIR/config.yaml" "$STAGE_DIR/config.yaml"; fi
  [[ -f "$STAGE_DIR/handler.py" ]] || { echo "ERROR: handler.py missing after copy"; exit 1; }
  (cd "$STAGE_DIR" && python _verify.py)
  rm -f "$ZIP_PATH"
  (cd "$STAGE_DIR" && ZIP_PATH="$ZIP_PATH" python _zip_stage.py)
  # Warn if Mach-O libs were included
  if command -v file >/dev/null 2>&1; then
    if find "$STAGE_DIR" -name "*.so" -print0 | xargs -0 file | grep -qi 'Mach-O'; then
      echo "WARNING: Detected macOS .so files. Rebuild with USE_DOCKER=1 for Lambda compatibility."
    fi
  fi
fi

echo "[build] done: $ZIP_PATH"
echo "Next: aws lambda update-function-code --function-name <name> --zip-file fileb://$ZIP_PATH"


