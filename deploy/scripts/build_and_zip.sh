#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
BUILD_DIR="$ROOT_DIR/build"
STAGE_DIR="$BUILD_DIR/src"
ZIP_PATH="$BUILD_DIR/package.zip"

echo "[build] cleaning $BUILD_DIR"
rm -rf "$BUILD_DIR" && mkdir -p "$STAGE_DIR" "$BUILD_DIR"

echo "[build] preparing requirements.txt"
if [[ -f "$ROOT_DIR/requirements.txt" ]]; then
  cp "$ROOT_DIR/requirements.txt" "$STAGE_DIR/requirements.txt"
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

echo "[build] creating virtualenv in $STAGE_DIR/.venv"
python3 -m venv "$STAGE_DIR/.venv"
source "$STAGE_DIR/.venv/bin/activate"
python -m pip install --upgrade pip >/dev/null
echo "[build] installing python deps into $STAGE_DIR (zip root of package)"
python -m pip install -r "$STAGE_DIR/requirements.txt" -t "$STAGE_DIR"

echo "[build] copying project package"
mkdir -p "$STAGE_DIR/reddit_researcher"
rsync -a --exclude '__pycache__' --exclude '*.pyc' "$ROOT_DIR/src/reddit_researcher/" "$STAGE_DIR/reddit_researcher/"

echo "[build] adding lambda handler"
cp "$ROOT_DIR/deploy/lambda/handler.py" "$STAGE_DIR/handler.py"

echo "[build] zipping to $ZIP_PATH"
rm -f "$ZIP_PATH"
(cd "$STAGE_DIR" && zip -qr "$ZIP_PATH" . -x ".venv/*")
echo "[build] done: $ZIP_PATH"


