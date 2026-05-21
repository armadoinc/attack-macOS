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
from urllib.parse import quote

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

GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY", "darmado/attack-macOS")
GITHUB_DEFAULT_REF = os.environ.get("GITHUB_REF", "main")

GITHUB_BLOB_URL_FMT = "https://github.com/{owner}/{repo}/blob/{ref}/"
GITHUB_RAW_URL_FMT = "https://raw.githubusercontent.com/{owner}/{repo}/{ref}/"

REPO_PROC_CONFIG_DIR = "attackmacos/core/config"
REPO_TTP_ROOT = "attackmacos/ttp"
REPO_TTP_SHELL_SUBDIR = "shell"
REPO_SHELL_SUFFIX = ".sh"
REPO_CONFIG_SUFFIX = ".yml"
REPO_UNKNOWN_TACTIC_DIR = "unknown"

SITE_DOCS_SEGMENT = "docs"
SITE_PROCEDURES_SEGMENT = "procedures"
SITE_ASSETS_SEGMENT = "assets"
SITE_DATA_SEGMENT = "data"
SITE_PROCEDURES_JSON = "procedures.json"

OUT_INDEX = "index.html"
OUT_BROWSE = "browse.html"
OUT_DOCS_ROOT = "docs"
OUT_PROCEDURES_ROOT = "procedures"

MARKDOWN_EXT = ".md"
HTML_EXT = ".html"

SITE_LOGO_URL = os.environ.get(
    "SITE_LOGO_URL",
    "https://github.com/user-attachments/assets/03a5c7dc-9dd6-49f9-a58b-2fdcdb6596f6",
)

INTENT_SHORT_LIMIT = 56

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

MD_TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def _tactic_dir(tactic: str) -> str:
    return TACTIC_MAP.get(tactic, tactic.lower().replace(" ", "_"))


def _github_owner_repo() -> tuple[str, str]:
    owner, repo = GITHUB_REPO.split("/", 1)
    return owner, repo


def _github_url(fmt: str, path_in_repo: str) -> str:
    owner, repo = _github_owner_repo()
    base = fmt.format(owner=owner, repo=repo, ref=GITHUB_DEFAULT_REF)
    return base + path_in_repo.lstrip("/")


def _github_blob(path_in_repo: str) -> str:
    return _github_url(GITHUB_BLOB_URL_FMT, path_in_repo)


def _github_raw(path_in_repo: str) -> str:
    return _github_url(GITHUB_RAW_URL_FMT, path_in_repo)


def _repo_path_proc_config(config_filename: str) -> str:
    return f"{REPO_PROC_CONFIG_DIR}/{config_filename}"


def _repo_path_shell_script(tactic_dir: str, procedure_name: str) -> str:
    return "/".join(
        (
            REPO_TTP_ROOT,
            tactic_dir,
            REPO_TTP_SHELL_SUBDIR,
            f"{procedure_name}{REPO_SHELL_SUFFIX}",
        )
    )


def _site_url(*segments: str) -> str:
    parts = [SITE_PREFIX.strip("/")] if SITE_PREFIX else []
    parts.extend(s.strip("/") for s in segments if s and s.strip("/"))
    return "/" + "/".join(parts)


def _quote_seg(seg: str) -> str:
    return quote(seg, safe="-._~")


def _doc_href(rel: Path) -> str:
    parts = rel.as_posix().split("/")
    out_parts = parts[:-1] + [parts[-1].replace(MARKDOWN_EXT, HTML_EXT)]
    return _site_url(SITE_DOCS_SEGMENT, *(_quote_seg(p) for p in out_parts))


def _procedure_page_href(slug: str) -> str:
    return _site_url(SITE_PROCEDURES_SEGMENT, f"{slug}{HTML_EXT}")


def _doc_output_rel(rel: Path) -> Path:
    return Path(OUT_DOCS_ROOT) / Path(*rel.parts[:-1]) / (rel.stem + HTML_EXT)


def _platform_display(platform_value: object) -> str:
    if isinstance(platform_value, list):
        return ", ".join(str(x) for x in platform_value)
    if platform_value:
        return str(platform_value)
    return ""


def _intent_short(intent: str) -> str:
    line = " ".join(intent.split())
    if len(line) <= INTENT_SHORT_LIMIT:
        return line
    return line[: INTENT_SHORT_LIMIT - 1].rstrip() + "…"


def _read_repo_text(rel_path: str) -> str | None:
    path = REPO_ROOT / rel_path
    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _map_procedure_row(data: dict, config_filename: str) -> dict:
    procedure_name = str(data.get("procedure_name", "")).strip()
    tactic = str(data.get("tactic", "")).strip()
    tactic_dir = _tactic_dir(tactic) if tactic else REPO_UNKNOWN_TACTIC_DIR
    config_path = _repo_path_proc_config(config_filename)
    script_path = _repo_path_shell_script(tactic_dir, procedure_name)
    intent = str(data.get("intent", "")).strip()
    return {
        "procedure_name": procedure_name,
        "slug": procedure_name,
        "tactic": tactic,
        "tactic_key": tactic.lower(),
        "ttp_id": str(data.get("ttp_id", "")).strip(),
        "author": str(data.get("author", "")).strip(),
        "intent": intent,
        "intent_short": _intent_short(intent),
        "version": str(data.get("version", "")).strip(),
        "guid": str(data.get("guid", "")).strip(),
        "created": str(data.get("created", "")).strip(),
        "updated": str(data.get("updated", "")).strip(),
        "credit": str(data.get("credit", "")).strip(),
        "platform_display": _platform_display(data.get("platform")),
        "yaml_path": config_path,
        "script_path": script_path,
        "script_href": _github_raw(script_path),
        "yaml_href": _github_blob(config_path),
        "page_href": _procedure_page_href(procedure_name),
    }


def _map_doc_nav_item(rel: Path, title: str) -> dict:
    return {
        "href": _doc_href(rel),
        "title": title,
        "sort": rel.as_posix().lower(),
        "rel": rel.as_posix(),
    }


def load_procedures() -> list[dict]:
    rows: list[dict] = []
    for config_file in sorted(PROC_DIR.glob(f"*{REPO_CONFIG_SUFFIX}")):
        try:
            raw = config_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict) or "procedure_name" not in data:
            continue
        if not str(data.get("procedure_name", "")).strip():
            continue
        rows.append(_map_procedure_row(data, config_file.name))
    rows.sort(key=lambda row: row["procedure_name"].lower())
    return rows


def build_doc_nav() -> list[dict]:
    nav: list[dict] = []
    for path in sorted(DOCS.rglob(f"*{MARKDOWN_EXT}")):
        if "public" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = path.relative_to(DOCS)
        title = rel.as_posix()
        match = MD_TITLE_RE.search(text)
        if match:
            title = match.group(1).strip()
        nav.append(_map_doc_nav_item(rel, title))
    nav.sort(key=lambda item: item["sort"])
    return nav


def render_md_to_html(text: str) -> str:
    return markdown(
        text,
        extensions=["fenced_code", "tables", "nl2br"],
        output_format="html5",
    )


def write_procedures_json(procedures: list[dict]) -> None:
    data_dir = OUT / SITE_ASSETS_SEGMENT / SITE_DATA_SEGMENT
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / SITE_PROCEDURES_JSON).write_text(
        json.dumps(procedures, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def copy_static() -> None:
    dest = OUT / SITE_ASSETS_SEGMENT
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
            site_logo_url=SITE_LOGO_URL,
            **ctx,
        )
        out_path = OUT / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html_out, encoding="utf-8")

    render("home.html", OUT_INDEX)
    render("browse.html", OUT_BROWSE)

    proc_tpl = env.get_template("procedure.html")
    for proc in procedures:
        procedure_name = proc["procedure_name"]
        md_path = PROC_DOCS / f"{procedure_name}{MARKDOWN_EXT}"
        yaml_raw = _read_repo_text(proc["yaml_path"]) or ""
        script_raw = _read_repo_text(proc["script_path"]) or ""
        has_script = bool(script_raw)
        default_view = "script" if has_script else "yaml"
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
            site_logo_url=SITE_LOGO_URL,
            proc=proc,
            yaml_raw=yaml_raw,
            script_raw=script_raw,
            has_script=has_script,
            default_view=default_view,
            body_html=Markup(body_html) if body_html else None,
            has_proc_doc=bool(body_html),
        )
        out_path = OUT / OUT_PROCEDURES_ROOT / f"{proc['slug']}{HTML_EXT}"
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
        body = Markup(render_md_to_html(md_text))
        html_out = doc_tpl.render(
            site_prefix=SITE_PREFIX,
            procedures=procedures,
            tactics=tactics,
            doc_nav=doc_nav,
            github_repo=GITHUB_REPO,
            site_logo_url=SITE_LOGO_URL,
            doc_title=item["title"],
            body_html=body,
            current_href=item["href"],
        )
        out_path = OUT / _doc_output_rel(rel)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html_out, encoding="utf-8")

    print(f"Wrote site to {OUT} ({len(procedures)} procedures, prefix={SITE_PREFIX!r})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
