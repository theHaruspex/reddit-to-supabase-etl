#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
BUILD_DIR="$ROOT_DIR/build"
ZIP_PATH="$BUILD_DIR/package.zip"

echo "[build] cleaning $BUILD_DIR"
rm -rf "$BUILD_DIR" && mkdir -p "$BUILD_DIR"

echo "[build] preparing requirements.txt"
if [[ -f "$ROOT_DIR/requirements.txt" ]]; then
  cp "$ROOT_DIR/requirements.txt" "$BUILD_DIR/requirements.txt"
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
out = Path('build/requirements.txt')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text('\n'.join(deps) + '\n')
print('[build] wrote', out)
PY
fi

echo "[build] installing python deps into build/ (zip root)"
python3 -m venv "$BUILD_DIR/.venv"
source "$BUILD_DIR/.venv/bin/activate"
python -m pip install --upgrade pip >/dev/null
python -m pip install -r "$BUILD_DIR/requirements.txt" -t "$BUILD_DIR"

echo "[build] copying project package"
mkdir -p "$BUILD_DIR/reddit_researcher"
rsync -a --exclude '__pycache__' --exclude '*.pyc' "$ROOT_DIR/src/reddit_researcher/" "$BUILD_DIR/reddit_researcher/"

echo "[build] adding lambda handler"
cp "$ROOT_DIR/deploy/lambda/handler.py" "$BUILD_DIR/handler.py"

echo "[build] zipping to $ZIP_PATH"
(cd "$BUILD_DIR" && zip -qr "$ZIP_PATH" .)
echo "[build] done: $ZIP_PATH"


