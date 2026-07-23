# Brief: Align release and MCP registry infrastructure with local-delegate

## Problem

The project publishes to PyPI from a GitHub Release, but it has no continuous-integration
workflow, lockfile, pre-commit policy, MCP Registry descriptor, registry publication step, or
documented release checklist. Its sibling `local-delegate` has those development and community
conventions and has been published manually to the official MCP Registry.

## Desired outcome

A version tag drives a reproducible, secretless PyPI and official MCP Registry release, while
pushes and pull requests run the same lint, format, test, lockfile, and secret checks developers
run locally. Documentation and community files explain the supported workflow.

## In scope

- GitHub Actions for CI and tag-driven PyPI/MCP Registry publication.
- `server.json`, PyPI ownership proof in README, and synchronized release versions.
- `uv` lockfile/dev tooling, pre-commit hooks, tests, and community contribution templates.
- Release documentation and a safer release helper.

## Out of scope

- Publishing a new package version or creating/pushing a tag in this change.
- Changing transcription behavior or optional backend dependency semantics.
- Modifying the sibling `local-delegate` repository or repository-level branch protection.

## Constraints and risks

- Preserve the existing PyPI trusted-publisher environment named `pypi`.
- MCP Registry GitHub OIDC requires `id-token: write` and the `io.github.ZahiriNatZuke/*`
  namespace.
- PyPI ownership validation requires the exact `mcp-name` marker in the published README.
- Existing untracked `.codex/` and `AGENTS.md` are user-owned and must remain untouched.

## Open questions

- None. The official registry supports PyPI and GitHub OIDC; the next package release will be the
  first registry-publishable release because PyPI 1.1.1 lacks the ownership marker.
