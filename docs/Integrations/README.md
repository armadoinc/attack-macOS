# Integrations (third-party)

Documentation for **how this repository connects to external products and services** (CLIs, hosted APIs, plugins). Execution procedures for TTPs on endpoints live elsewhere (`docs/Guides/`, `docs/Standards/`).

## Security baseline

Start here for **any new integration**:

- **[Third-party integrations — security baseline](third_party_security.md)** — generic requirements (secrets, subprocess, least privilege, documentation).

## Per-integration docs

| Topic | Document |
|-------|----------|
| **GitHub** (`gh`, issue presets, tokens) | [github_repo_interaction.md](github_repo_interaction.md) |
| **Caldera** (attack-macOS plugin overview) | [Caldera plugin](../../integrations/CALDERA.md) (repo root `integrations/`) |

## Tooling entrypoints

| Integration | Code / config |
|---------------|----------------|
| GitHub Issues | `cicd/gh/github_issues.py`, `cicd/gh/known_issues.yaml`, `.github/issue_bodies/` |

When you add a new vendor touchpoint, add a row to **`third_party_security.md`** and either a new page under **`docs/Integrations/`** or a clearly linked doc under `integrations/` with a pointer from this README.

## Design drafts

- [Procedure YAML SDK (read-first, PyPI later)](../Design/procedure_yaml_sdk_design.md) — template + validate + serialize; builders stay maintainer-owned.

---
Last modified: 2026-05-15
