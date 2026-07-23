#!/usr/bin/env python3
"""Validate release metadata shared by PyPI and the official MCP Registry."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_NAME = "io.github.ZahiriNatZuke/whisper-transcribe-mcp"
PACKAGE_NAME = "whisper-transcribe-mcp"


def project_version() -> str:
    manifest = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"$', manifest, flags=re.MULTILINE)
    if match is None:
        raise ValueError("Could not find project.version in pyproject.toml")
    return match.group(1)


def validate(tag: str | None = None, schema_path: Path | None = None) -> list[str]:
    errors: list[str] = []
    version = project_version()
    server = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    package = server.get("packages", [{}])[0]
    expected = {
        "server.json version": server.get("version"),
        "server.json package version": package.get("version"),
    }
    for label, actual in expected.items():
        if actual != version:
            errors.append(f"{label} is {actual!r}; expected {version!r}")

    if tag is not None and tag != f"v{version}":
        errors.append(f"tag is {tag!r}; expected 'v{version}'")
    if server.get("name") != SERVER_NAME:
        errors.append(f"server name must be {SERVER_NAME!r}")
    if package.get("registryType") != "pypi" or package.get("identifier") != PACKAGE_NAME:
        errors.append("server.json must reference the whisper-transcribe-mcp PyPI package")
    if len(server.get("description", "")) > 100:
        errors.append("server.json description exceeds the Registry's 100-character limit")
    if f"mcp-name: {SERVER_NAME}" not in readme:
        errors.append("README.md is missing the PyPI MCP Registry ownership marker")

    if schema_path is not None:
        from jsonschema import Draft7Validator

        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        for error in sorted(
            Draft7Validator(schema).iter_errors(server), key=lambda item: list(item.path)
        ):
            location = ".".join(str(part) for part in error.path) or "server.json"
            errors.append(f"schema error at {location}: {error.message}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", help="Git tag to compare, for example v1.2.3")
    parser.add_argument("--schema", type=Path, help="Optional local server.schema.json")
    args = parser.parse_args()

    errors = validate(args.tag, args.schema)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Release metadata is consistent for {project_version()}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
