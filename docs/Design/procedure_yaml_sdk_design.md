# Procedure YAML SDK — design (read-first, PyPI later)

## Purpose

Describe a **small, read-oriented** Python package that helps authors produce **valid procedure YAML** for this repository **without** re-implementing shell/JXA/Swift builders. **Build, validate, and merge policy stay with maintainers** (existing `cicd/build/*`, PR review, and inventory audits).

## Non-goals (v0)

- **No** client-side execution of generated TTP scripts.
- **No** replacement for `procedure_shell.py` / `procedure_jxa.py` as the source of truth for emitted scripts.
- **No** obligation for maintainers to auto-merge contributor PRs created by the tool.

## Audience

External contributors and internal engineers who want a guided path from “empty idea” to “paste-ready YAML draft.”

## Principles

1. **Templates over magic** — Load `attackmacos/core/templates/procedure.yml` (or a trimmed JSON Schema fragment) and expose **typed helpers** / **builder functions** that return nested `dict` structures matching `procedure.schema.json`.
2. **Validate before serialize** — Run **`jsonschema`** against `attackmacos/core/schemas/procedure.schema.json` (same as CI expectations) and return structured errors (path + message).
3. **Serialize only** — Output **YAML** (PyYAML) with stable key order where practical; no shell/JXA emission in v0.
4. **Optional PR helper (later)** — A separate opt-in module or CLI flag could shell out to **`gh pr create`** with a body template; must respect `docs/Integrations/github_repo_interaction.md` (tokens, no secrets in YAML).

## Suggested package layout (PyPI)

```
attackmacos-procedure/          # working name; TBD before PyPI publish
  pyproject.toml
  README.md
  src/
    attackmacos_procedure/
      __init__.py
      template.py      # load embedded copy of procedure.yml or path from env
      model.py         # thin dataclasses OR TypedDict for procedure top-level keys
      validate.py      # jsonschema.validate(instance, schema)
      dump.py          # yaml.safe_dump with width
      cli.py           # optional: `attackmacos-proc init > draft.yml`
```

**Versioning:** follow SemVer; 0.x until the schema surface is considered stable.

## Public API (sketch)

| Function | Behavior |
|----------|----------|
| `load_template()` | Return nested `dict` mirroring empty `procedure.yml` (from vendored snapshot or `ATTACKMACOS_TEMPLATE_PATH`). |
| `validate_procedure(data: dict) -> None` | Raise `ProcedureValidationError` with JSON Schema errors. |
| `dump_procedure(data: dict) -> str` | Return YAML string suitable for saving under `attackmacos/core/config/`. |
| `minimal_shell_example()` | Optional: return a tiny valid `functions` / `arguments` example for copy-paste. |

## Relationship to PyLOOBins

**[PyLOOBins](https://www.loobins.io/docs/api/pyloobins/)** models **LOOBin** YAML. This SDK models **attack-macOS procedure** YAML. If a workflow starts from a LOOBin, the path is: **PyLOOBins / catalog → human or `convert_loobin_to_procedure.py` → procedure YAML → (optional) this SDK to refine/validate**. The SDK should **not** try to be a second LOOBin parser unless we add an explicit optional dependency later.

## PR automation (future, opt-in)

- **Inputs:** fork URL or assumes `origin`, branch name, title, path to YAML.
- **Flow:** `gh repo fork` (if needed) → copy file → `gh pr create --body-file …`.
- **Guardrails:** document that maintainers run builders and `run_local_qa.sh`; bot-created PRs are still reviewed like any other.

## Open questions

- **Ship schema in wheel** vs read from installed `attackmacos` package path (PyPI package might not ship full repo).
- **Python floor** (3.10+ to match maintainer tooling).
- **Name collision** on PyPI — search before registration.

---
Last modified: 2026-05-15
