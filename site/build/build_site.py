#!/usr/bin/env python3
"""
Build static GitHub Pages output into site/public/.

Reads: docs/**/*.md, attackmacos/core/config/*.yml, docs/Procedures/<name>.md
See: docs/Design/website_docs_pipeline.md

Run from repo root:
  pip install -r site/build/requirements.txt
  python3 site/build/build_site.py
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown import markdown
from markupsafe import Markup

REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_ROOT = REPO_ROOT / "site"
OUT = SITE_ROOT / "public"
BUILD = Path(__file__).resolve().parent
TEMPLATES = BUILD / "templates"
STATIC = BUILD / "static"
PROC_DIR = REPO_ROOT / "attackmacos" / "core" / "config"
DOCS = REPO_ROOT / "docs"
PROC_DOCS = DOCS / "Procedures"

SITE_PREFIX = os.environ.get("SITE_PREFIX", "/attack-macOS").rstrip("/") or ""

TACTIC_MAP = {
    "Discovery": "discovery",
    "Defense Evasion": "defense_evasion",
    "Persistence": "persistence",
    "Collection": "collection",
    "Credential Access": "credential_access",
    "Execution": "execution",
    "Initial Access": "initial_access",
    "Lateral Movement": "lateral_movement",
    "Privilege Escalation": "privilege_escalation",
    "Command and Control": "command_and_control",
    "Exfiltration": "exfiltration",
    "Impact": "impact",
}

GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY", "darmado/attack-macOS")


def _tactic_dir(tactic: str) -> str:
    return TACTIC_MAP.get(tactic, tactic.lower().replace(" ", "_"))


def _github_blob(path_in_repo: str) -> str:
    owner, repo = GITHUB_REPO.split("/", 1)
    return f"https://github.com/{owner}/{repo}/blob/main/{path_in_repo}"


def _github_raw(path_in_repo: str) -> str:
    owner, repo = GITHUB_REPO.split("/", 1)
    return f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path_in_repo}"


def load_procedures() -> list[dict]:
    rows: list[dict] = []
    for f in sorted(PROC_DIR.glob("*.yml")):
        try:
            raw = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict) or "procedure_name" not in data:
            continue
        pn = str(data.get("procedure_name", "")).strip()
        if not pn:
            continue
        tactic = str(data.get("tactic", "")).strip()
        tdir = _tactic_dir(tactic) if tactic else "unknown"
        rel_script = f"attackmacos/ttp/{tdir}/shell/{pn}.sh"
        plat = data.get("platform")
        if isinstance(plat, list):
            platform_display = ", ".join(str(x) for x in plat)
        elif plat:
            platform_display = str(plat)
        else:
            platform_display = ""
        rows.append(
            {
                "procedure_name": pn,
                "slug": pn,
                "tactic": tactic,
                "tactic_key": tactic.lower(),
                "ttp_id": str(data.get("ttp_id", "")).strip(),
                "author": str(data.get("author", "")).strip(),
                "intent": str(data.get("intent", "")).strip(),
                "version": str(data.get("version", "")).strip(),
                "guid": str(data.get("guid", "")).strip(),
                "created": str(data.get("created", "")).strip(),
                "updated": str(data.get("updated", "")).strip(),
                "credit": str(data.get("credit", "")).strip(),
                "platform_display": platform_display,
                "yaml_path": f"attackmacos/core/config/{f.name}",
                "script_href": _github_raw(rel_script),
                "yaml_href": _github_blob(f"attackmacos/core/config/{f.name}"),
            }
        )
    return rows


def _doc_href(rel: Path) -> str:
    parts = rel.as_posix().split("/")
    out_parts = parts[:-1] + [parts[-1].replace(".md", ".html")]
    return SITE_PREFIX + "/docs/" + "/".join(_quote_seg(p) for p in out_parts)


def _quote_seg(seg: str) -> str:
    from urllib.parse import quote

    return quote(seg, safe="-._~")


def build_doc_nav() -> list[dict]:
    nav: list[dict] = []
    for path in sorted(DOCS.rglob("*.md")):
        if "public" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = path.relative_to(DOCS)
        title = rel.as_posix()
        m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        if m:
            title = m.group(1).strip()
        href = _doc_href(rel)
        nav.append({"href": href, "title": title, "sort": rel.as_posix().lower(), "rel": rel.as_posix()})
    nav.sort(key=lambda x: x["sort"])
    return nav


def render_md_to_html(text: str) -> str:
    return markdown(
        text,
        extensions=["fenced_code", "tables", "nl2br"],
        output_format="html5",
    )


def write_procedures_json(procedures: list[dict]) -> None:
    data = OUT / "assets" / "data"
    data.mkdir(parents=True, exist_ok=True)
    (data / "procedures.json").write_text(
        json.dumps(procedures, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def copy_static() -> None:
    dest = OUT / "assets"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(STATIC / "app.css", dest / "app.css")
    shutil.copy2(STATIC / "app.js", dest / "app.js")


def main() -> int:
    if not DOCS.is_dir() or not PROC_DIR.is_dir():
        print("Run from repository root (docs/ and attackmacos/core/config/ required).", file=sys.stderr)
        return 1

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    procedures = load_procedures()
    tactics = sorted({p["tactic"] for p in procedures if p.get("tactic")})
    doc_nav = build_doc_nav()
    write_procedures_json(procedures)
    copy_static()

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    def render(name: str, out_rel: str, **ctx) -> None:
        tpl = env.get_template(name)
        html_out = tpl.render(
            site_prefix=SITE_PREFIX,
            procedures=procedures,
            tactics=tactics,
            doc_nav=doc_nav,
            github_repo=GITHUB_REPO,
            **ctx,
        )
        out_path = OUT / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html_out, encoding="utf-8")

    render("home.html", "index.html")
    render("browse.html", "browse.html")

    proc_tpl = env.get_template("procedure.html")
    for p in procedures:
        pn = p["procedure_name"]
        md_path = PROC_DOCS / f"{pn}.md"
        body_html: str | None = None
        if md_path.is_file():
            try:
                body_html = render_md_to_html(md_path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                body_html = None
        html_out = proc_tpl.render(
            site_prefix=SITE_PREFIX,
            procedures=procedures,
            tactics=tactics,
            doc_nav=doc_nav,
            github_repo=GITHUB_REPO,
            proc=p,
            body_html=Markup(body_html) if body_html else None,
            has_proc_doc=bool(body_html),
        )
        out_path = OUT / "procedures" / f"{p['slug']}.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html_out, encoding="utf-8")

    doc_tpl = env.get_template("doc.html")
    for item in doc_nav:
        rel = Path(item["rel"])
        path = DOCS / rel
        try:
            md_text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        current_href = item["href"]
        body = Markup(render_md_to_html(md_text))
        html_out = doc_tpl.render(
            site_prefix=SITE_PREFIX,
            procedures=procedures,
            tactics=tactics,
            doc_nav=doc_nav,
            github_repo=GITHUB_REPO,
            doc_title=item["title"],
            body_html=body,
            current_href=current_href,
        )
        out_rel = Path("docs") / Path(*rel.parts[:-1]) / (rel.stem + ".html")
        out_path = OUT / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html_out, encoding="utf-8")

    print(f"Wrote site to {OUT} ({len(procedures)} procedures, prefix={SITE_PREFIX!r})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
