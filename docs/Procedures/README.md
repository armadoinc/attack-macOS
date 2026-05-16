# Procedure-specific documentation (`docs/Procedures/`)

Optional **Markdown** per shell procedure, keyed by **`procedure_name`** from `attackmacos/core/config/<anything>.yml`.

## Naming

| YAML `procedure_name` | Markdown file |
|----------------------|----------------|
| `system_info` | `docs/Procedures/system_info.md` |
| `find_account_defaults` | `docs/Procedures/find_account_defaults.md` |

Filenames are **lowercase slugs** exactly matching `procedure_name`.

## When to add a file

- Operator notes, safety cautions, parameter examples, or detection discussion.
- Content that is awkward to keep inside YAML but should ship **next to** the procedure on the website.

If a file is missing, the site still publishes a **procedure page** from YAML only.

## Website build

These files are consumed by `site/build/build_site.py` (see `docs/Design/website_docs_pipeline.md`).

---
Last modified: 2026-05-15
