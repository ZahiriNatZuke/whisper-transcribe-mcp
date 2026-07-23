# Research: Align release and MCP registry infrastructure with local-delegate

## Current behavior

- `.github/workflows/publish.yml` builds with `pip` and publishes to PyPI only when a GitHub
  Release is published; there is no CI workflow.
- `release.sh` changes only `pyproject.toml`, commits/pushes, and creates a GitHub Release.
- The project has no `server.json`, `uv.lock`, `.python-version`, pre-commit configuration, tests,
  changelog, contribution guide, or GitHub issue/PR templates.
- `local-delegate` uses `uv`, checks its lockfile, runs Ruff/pytest/gitleaks, has pre-commit hooks,
  a `server.json`, community files, and a documented tag release procedure.
- Live Registry API lookup returned active `local-delegate` versions 0.1.1, 0.8.1, and 0.9.0;
  its publication is currently manual because its workflow contains no `mcp-publisher` step.
- Official MCP Registry docs (checked 2026-07-23) specify PyPI ownership via an exact
  `mcp-name: <server-name>` README marker and GitHub Actions authentication through
  `mcp-publisher login github-oidc` with `id-token: write`.

## Impact map

| Area | Current responsibility | Expected impact | Evidence |
| --- | --- | --- | --- |
| Packaging | `pyproject.toml`, Hatchling | Add dev group, metadata, Ruff/pytest config; retain runtime extras | Manifest and imported modules audited |
| Dependency resolution | Ad-hoc pip install | Add committed `uv.lock` and Python pin | `local-delegate` convention and CI reproducibility |
| Quality | No automated checks/tests | Add CI, pre-commit, and focused unit tests | No `tests/` or `ci.yml` exists |
| Release | GitHub Release event -> PyPI | Tag -> validate -> PyPI -> Registry via OIDC | Existing workflow/helper and official Registry Actions guide |
| Discovery | Glama metadata only | Add official `server.json` and README ownership marker | Official PyPI package-type guide |
| Community/docs | README only | Add changelog, contribution/conduct docs, templates, publishing guide | Sibling repository inventory |

## Existing conventions

- `uv` for environment, lock, build, and publish operations.
- Ruff default rules plus import sorting, pytest under `tests/`, gitleaks in pre-commit and CI.
- Semantic versions aligned across `pyproject.toml`, `server.json`, and the tag.
- PyPI Trusted Publishing with the existing `pypi` environment and no stored token.

## Dependencies and integrations

- New development-only packages: pytest, Ruff, and pre-commit. Socket scores were all above 0.7
  (minimum category scores: pytest 0.86, pre-commit 0.93, Ruff 1.0).
- Existing runtime imports were checked: `fastmcp`, optional `faster_whisper`, optional `openai`,
  and Python standard library modules.
- External systems: PyPI, GitHub Actions/Releases/OIDC, official MCP Registry, GitHub namespace.

## Risks and unknowns

- Confirmed: current PyPI 1.1.1 README lacks the ownership marker, so that already-published
  artifact cannot validate a first Registry publication.
- Confirmed: Registry server descriptions are limited to 100 characters and published versions
  are immutable.
- Risk: PyPI metadata propagation can lag after upload; publication must retry or wait before the
  Registry validation step.
- Risk: downloading `mcp-publisher` from `latest` is mutable; pin and checksum its release asset.
