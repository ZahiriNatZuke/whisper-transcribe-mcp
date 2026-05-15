#!/usr/bin/env bash
set -e

VERSION=$1

if [[ -z "$VERSION" ]]; then
  echo "Usage: ./release.sh <version>  (e.g. ./release.sh 0.3.0)"
  exit 1
fi

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: version must be in X.Y.Z format"
  exit 1
fi

echo "Releasing v$VERSION..."

sed -i '' "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml

git add pyproject.toml
git commit -m "chore: bump version to $VERSION"
git push

gh release create "v$VERSION" --title "v$VERSION" --generate-notes

echo "Done! GitHub Actions will publish to PyPI automatically."
echo "Track progress: https://github.com/ZahiriNatZuke/whisper-transcribe-mcp/actions"
