# Publishing and release process

## Versioning

The project uses Semantic Versioning. Every release aligns the version in `pyproject.toml`,
`uv.lock`, `server.json`, the package entry inside `server.json`, and tag `vX.Y.Z`.

## One-time setup

Configure a PyPI Trusted Publisher for `whisper-transcribe-mcp` with these values:

| Field | Value |
| --- | --- |
| Owner | `ZahiriNatZuke` |
| Repository | `whisper-transcribe-mcp` |
| Workflow | `publish.yml` |
| Environment | `pypi` |

The GitHub repository already uses the `pypi` environment. The official MCP Registry needs no
dedicated secret: the workflow requests a short-lived GitHub OIDC identity. The server namespace
must remain `io.github.ZahiriNatZuke/whisper-transcribe-mcp`.

## Prepare and publish a release

1. Move the relevant `CHANGELOG.md` entries from `Unreleased` into a `## [X.Y.Z] - YYYY-MM-DD`
   section and update comparison links.
2. Commit all other work so tracked files are clean.
3. Run `./release.sh X.Y.Z` from `main`.

The helper updates both manifests, regenerates `uv.lock`, runs metadata validation, Ruff, pytest,
and a package build, then commits and pushes `main`. It waits for the exact CI run to pass before
creating and pushing the version tag and creating the GitHub Release.

The tag starts `.github/workflows/publish.yml`, which:

1. Revalidates the lockfile, tag, manifests, and official `server.json` schema.
2. Runs Ruff and pytest and builds the wheel/source distribution.
3. Publishes idempotently to PyPI using Trusted Publishing via `pypa/gh-action-pypi-publish`,
   which also uploads PEP 740 provenance attestations for the wheel and sdist.
4. Waits until PyPI exposes the new metadata.
5. Downloads a pinned, checksum-verified `mcp-publisher`, authenticates with GitHub OIDC, and
   publishes the same version to the official MCP Registry.

No PyPI token or MCP Registry token is stored in GitHub Secrets. Every third-party action is
pinned to a full commit SHA; Dependabot proposes updates.

After a release, confirm the provenance is available:

```bash
curl -s -H "Accept: application/vnd.pypi.integrity.v1+json"   https://pypi.org/integrity/whisper-transcribe-mcp/X.Y.Z/whisper_transcribe_mcp-X.Y.Z-py3-none-any.whl/provenance
```

If a downstream step fails after PyPI has accepted the package, repair the workflow on `main` and
retry the same immutable release without moving its tag:

```bash
gh workflow run publish.yml -f tag=vX.Y.Z
```

The publish steps are idempotent: existing PyPI files and an existing MCP Registry version are
detected and skipped.

## Registry ownership and first publication

The Registry verifies a PyPI package by reading this exact marker from the README published on
PyPI:

```text
mcp-name: io.github.ZahiriNatZuke/whisper-transcribe-mcp
```

Version 1.1.1 predates that marker, so it cannot establish the Registry entry. The next released
version will be the first one eligible for automated Registry publication.

Verify a successful publication with:

```bash
curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.ZahiriNatZuke%2Fwhisper-transcribe-mcp"
```

Registry versions are immutable. Correct bad metadata with a new version; do not try to overwrite
an already-published descriptor.
