#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-}"

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Usage: ./release.sh <version>  (for example: ./release.sh 1.2.0)" >&2
  exit 1
fi

cd "$(git rev-parse --show-toplevel)"

if [[ "$(git branch --show-current)" != "main" ]]; then
  echo "Error: releases must be prepared from main." >&2
  exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Error: tracked files contain uncommitted changes." >&2
  exit 1
fi

if git rev-parse --verify --quiet "refs/tags/v$VERSION" >/dev/null; then
  echo "Error: tag v$VERSION already exists." >&2
  exit 1
fi

if ! grep -q "^## \[$VERSION\]" CHANGELOG.md; then
  echo "Error: add a CHANGELOG.md section named [$VERSION] before releasing." >&2
  exit 1
fi

VERSION="$VERSION" uv run python - <<'PY'
import json
import os
import re
from pathlib import Path

version = os.environ["VERSION"]
manifest_path = Path("pyproject.toml")
manifest = manifest_path.read_text(encoding="utf-8")
manifest_path.write_text(
    re.sub(r'^version = "[^"]+"$', f'version = "{version}"', manifest, count=1, flags=re.MULTILINE),
    encoding="utf-8",
)

server_path = Path("server.json")
server = json.loads(server_path.read_text(encoding="utf-8"))
server["version"] = version
server["packages"][0]["version"] = version
server_path.write_text(json.dumps(server, indent=2) + "\n", encoding="utf-8")
PY

uv lock
uv run python scripts/check_release_metadata.py --tag "v$VERSION"
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv build

git add pyproject.toml uv.lock server.json CHANGELOG.md
if ! git diff --cached --quiet; then
  git commit -m "release: prepare v$VERSION"
fi
git push origin main

head_sha="$(git rev-parse HEAD)"
run_id=""
for _ in {1..12}; do
  run_id="$(gh run list --workflow ci.yml --branch main --event push --limit 10 \
    --json databaseId,headSha --jq ".[] | select(.headSha == \"$head_sha\") | .databaseId" | head -n 1)"
  [[ -n "$run_id" ]] && break
  sleep 5
done

if [[ -z "$run_id" ]]; then
  echo "Error: could not find the CI run for $head_sha; no tag was created." >&2
  exit 1
fi

gh run watch "$run_id" --exit-status
git tag "v$VERSION"
git push origin "v$VERSION"
gh release create "v$VERSION" --verify-tag --title "v$VERSION" --generate-notes

echo "Release v$VERSION created. The Publish workflow will upload PyPI and MCP Registry metadata."
echo "Track it at: https://github.com/ZahiriNatZuke/whisper-transcribe-mcp/actions"
