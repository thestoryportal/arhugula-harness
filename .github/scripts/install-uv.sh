#!/usr/bin/env bash
# CI's uv bootstrap: the exact official PyPI wheel, hash-pinned, in an isolated venv
# built from the runner's python3. It replaces astral-sh/setup-uv, whose uv binary
# comes only from GitHub release assets — a route that returned HTTP 504 on every
# attempt on 2026-11-08 while PyPI stayed reachable. The job environment it leaves is
# the one setup-uv@v5 left for these jobs: ~/.local/bin and uv on PATH, UV_PYTHON, an
# activated workspace .venv, UV_CACHE_DIR under RUNNER_TEMP. The managed CPython still
# comes from uv's own interpreter download, as before.
set -euo pipefail

readonly uv_version=0.13.7
readonly python_version=3.12
readonly bootstrap="$RUNNER_TEMP/uv-bootstrap"
readonly uv_cache_dir="$RUNNER_TEMP/setup-uv-cache"

python3 -m venv "$bootstrap/venv"
# [LAW:one-source-of-truth] PyPI's published digests for uv 0.13.7: the CI runner's
# x86_64 manylinux wheel and the aarch64 one that lets this exact script run locally.
cat > "$bootstrap/requirements.txt" <<EOF
uv==$uv_version \\
    --hash=sha256:2c9bdc4a872b60a93c5f26c0791089ea11585a4f9d3b3c017d78eb8487505e25 \\
    --hash=sha256:08f16fd463926786b702b497473511deae4b3e17a2fa6d22180950d6059a120d
EOF
"$bootstrap/venv/bin/python" -m pip install --disable-pip-version-check --no-deps \
  --only-binary :all: --require-hashes -r "$bootstrap/requirements.txt"

# Only uv and uvx join PATH: the bootstrap venv's python and pip must not shadow the
# interpreter that later steps resolve.
mkdir "$bootstrap/bin"
ln -s "$bootstrap/venv/bin/uv" "$bootstrap/venv/bin/uvx" "$bootstrap/bin/"
# [LAW:no-silent-failure] Run the installed binary itself: a wrong or broken uv stops
# this step instead of surfacing as a confusing sync failure later.
reported=$("$bootstrap/bin/uv" --version)
echo "$reported"
if [[ "${reported%% (*}" != "uv $uv_version" ]]; then
  echo "::error::expected uv $uv_version, installed binary reports: $reported" >&2
  exit 1
fi

UV_PYTHON="$python_version" UV_CACHE_DIR="$uv_cache_dir" \
  "$bootstrap/bin/uv" venv --python "$python_version" .venv

{
  echo "UV_PYTHON=$python_version"
  echo "UV_CACHE_DIR=$uv_cache_dir"
  echo "VIRTUAL_ENV=$PWD/.venv"
} >> "$GITHUB_ENV"
# Each GITHUB_PATH line is prepended in turn, so the last line wins: the workspace
# .venv, then uv, then the uv tool bin dir — setup-uv's order.
{
  echo "$HOME/.local/bin"
  echo "$bootstrap/bin"
  echo "$PWD/.venv/bin"
} >> "$GITHUB_PATH"
