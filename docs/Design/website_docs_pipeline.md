# Website documentation pipeline

## Goal

One **maintainable** static site (GitHub Pages) that:

1. **Mirrors** human-written Markdown under `docs/` into browsable HTML.
2. Lists **every shell procedure** from `attackmacos/core/config/*.yml` with filters (tactic, author, `ttp_id`, etc.).
3. Gives **each procedure its own page**, combining **YAML metadata** with optional long-form Markdown at **`docs/Procedures/<procedure_name>.md`**.

**Vanilla** here means: **no React/Vue/Svelte**—plain HTML, CSS, and a small amount of JavaScript for filters and the nav toggle.

## Single source of truth (do not fork content by hand)

| Content | Source in git | Published form |
|---------|---------------|----------------|
| Guides, CICD, indexes, R&D, etc. | `docs/**/*.md` | HTML under `site/public/docs/...` (generated) |
| Procedure metadata | `attackmacos/core/config/*.yml` | `site/public/assets/data/procedures.json` + per-procedure HTML |
| Procedure narrative | `docs/Procedures/<procedure_name>.md` (optional) | Rendered inside the procedure page |
| Core function reference | `docs/Functions/Shell/*.md` | Mirrored like other docs |

**Never edit** `site/public/` by hand. It is **build output** only (ignored by git). Edit sources, then run the builder.

## Build command

From the repository root (after `pip install -r site/build/requirements.txt`):

```bash
python3 site/build/build_site.py
# output: site/public/
```

GitHub Actions runs the same command before `upload-pages-artifact`.

## Adding or updating content

### Docs mirror

- Add or change Markdown under `docs/` as you do today.
- Rebuild the site; the mirrored path preserves the directory tree (e.g. `docs/Guides/README.md` → `/docs/Guides/README.html`).

### Procedure pages (every script has a page)

- **Always:** metadata comes from the YAML in `attackmacos/core/config/`. The build skips files that do not contain `procedure_name`.
- **Optional narrative:** add `docs/Procedures/<procedure_name>.md` (same string as `procedure_name` in YAML, e.g. `system_info.md`).
- If the Markdown file is **missing**, the procedure page still exists and shows a short notice with links to the YAML on GitHub and the generated shell path.

### When to create `docs/Procedures/*.md`

Use it for **operator-facing** notes: intent, safety, parameters, detection ideas—anything that belongs next to the procedure but not inside the YAML. Keep YAML for **machine** fields; keep prose in Markdown.

## Layout (UX contract)

- **Left:** collapsible **hamburger** nav (CSS-only toggle) with scrollable lists.
- **Center:** page body.
- **Top center (browse / procedures):** **search** + **filters** (tactic, author, `ttp_id`) implemented as lightweight client-side filtering over `procedures.json`.
- **Responsive:** sidebar becomes an off-canvas drawer on small screens; content stays readable.

## Related files

- `site/build/build_site.py` — generator entrypoint.
- `site/build/requirements.txt` — build-only dependencies.
- `site/build/templates/` — Jinja2 HTML layouts.
- `site/build/static/` — `app.css`, `app.js` copied to `site/public/assets/`.
- `docs/Procedures/README.md` — contributor note for procedure Markdown.

## Future extensions

- Full-text search (e.g. Lunr or small WASM indexer) generated at build time.
- JXA procedure pages once YAML layout is stable and mirrored the same way.
- `SITE_PREFIX` env for custom domain at repo root (`""`) vs project Pages (`/attack-macOS`).

---
Last modified: 2026-05-15
