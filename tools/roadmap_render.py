#!/usr/bin/env python3
from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any

from roadmap_db import RoadmapDBError, connect, now_utc, prompt_row, summary_rows

def _wikilink_for_prompt(row: sqlite3.Row) -> str:
    return f"[[obsidian/Prompts/{row['prompt_id']} {row['slug']}|{row['prompt_id']} · {row['title']}]]"

def _table_wikilink(target: str, label: str) -> str:
    # Markdown tables treat a bare pipe inside an Obsidian wikilink as a
    # column separator. Escape only the pipe used for the link alias.
    return f"[[{target}\\|{label}]]"
def _fmt(value: Any) -> str:
    if value is None or value == "":
        return "—"
    return str(value).replace("|", "\\|").replace("\n", " ")

_FINAL_STATUS_OUTCOME = {
    "completed": "PASS",
    "failed": "FAIL",
    "blocked": "BLOCKED",
    "cancelled": "CANCELLED",
    "unknown": "UNKNOWN",
}

def _effective_outcome(row: sqlite3.Row | dict[str, Any]) -> Any:
    """Prefer the authoritative terminal roadmap state over stale telemetry."""
    return _FINAL_STATUS_OUTCOME.get(row["status"], row["last_outcome"])

_MANUAL_PREREQ_LABELS = {
    "revoke-pat": "revoca il vecchio PAT GitHub",
    "kuma-login": "rifai il login a Kuma",
}

def _manual_prerequisite_text(conn: sqlite3.Connection, prompt_id: str) -> str | None:
    rows = conn.execute(
        "SELECT tag FROM prompt_tags WHERE prompt_id=? AND tag LIKE 'manual-prerequisite:%' ORDER BY tag",
        (prompt_id,),
    ).fetchall()
    if not rows:
        return None
    labels = []
    for row in rows:
        code = str(row[0]).split(":", 1)[1]
        labels.append(_MANUAL_PREREQ_LABELS.get(code, code.replace("-", " ")))
    return ", ".join(labels)

def _runnable_now_text(
    conn: sqlite3.Connection,
    row: sqlite3.Row,
    unresolved_dependencies: list[sqlite3.Row],
) -> str:
    if row["status"] == "running":
        return "▶ In corso"
    if unresolved_dependencies:
        ids = ", ".join(str(dep[0]) for dep in unresolved_dependencies)
        return f"⏳ No — prima: {ids}"
    manual = _manual_prerequisite_text(conn, str(row["prompt_id"]))
    if manual:
        return f"⛔ No — prima: {manual}"
    return "✅ Sì"

def _prompt_links(conn: sqlite3.Connection, prompt_id: str, relation_sql: str, params: tuple[Any,...]) -> str:
    rows = conn.execute(relation_sql, params).fetchall()
    if not rows:
        return "—"
    bits=[]
    seen=set()
    for r in rows:
        target_id=str(r[0])
        if target_id in seen:
            continue
        seen.add(target_id)
        p=prompt_row(conn, target_id)
        bits.append(f"[[{p['prompt_id']} {p['slug']}|{p['prompt_id']}]]")
    return ", ".join(bits)

def reconcile_prompt_file_locations(repo: Path) -> int:
    """Keep prompt file directory consistent with terminal status without inventing files."""
    repo=Path(repo)
    conn=connect(repo)
    moved=0
    try:
        rows=conn.execute("SELECT prompt_id,status,current_path FROM prompts WHERE current_path<>''").fetchall()
        for row in rows:
            current=row["current_path"]
            src=repo/current
            if row["status"]=="completed":
                target_dir="completed"
            elif row["status"] in ("failed","blocked","cancelled","superseded","unknown"):
                target_dir="falliti"
            else:
                target_dir="prompts"
            if current.startswith(target_dir+"/"):
                continue
            if not src.is_file():
                continue
            dest_rel=f"{target_dir}/{src.name}"
            dest=repo/dest_rel
            dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists():
                raise RoadmapDBError(f"archive_destination_exists:{dest_rel}")
            src.rename(dest)
            conn.execute(
                "UPDATE prompts SET current_path=?,updated_at=? WHERE prompt_id=?",
                (dest_rel,now_utc(),row["prompt_id"]),
            )
            moved += 1
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return moved

def render(repo: Path) -> list[str]:
    repo = Path(repo)
    conn = connect(repo, writable=False)
    rows = summary_rows(conn)
    pending = [r for r in rows if r["status"] in ("pending","running")]

    roadmap_lines = [
        "# Roadmap",
        "",
        "> Generato da `roadmap.sqlite`. Non modificare manualmente.",
        "",
    ]
    for i, r in enumerate(pending, 1):
        roadmap_lines.append(f"{i}. [[{r['current_path'][:-3]}|{r['slug']}]]" if r["current_path"].endswith(".md") else f"{i}. {_wikilink_for_prompt(r)}")
    if not pending:
        roadmap_lines.append("_Nessun prompt pendente._")
    roadmap_lines.append("")
    (repo/"roadmap.md").write_text("\n".join(roadmap_lines), encoding="utf-8")

    spieg = [
        "# Spiegazioni della roadmap",
        "",
        "> Generato da `roadmap.sqlite`. Le spiegazioni sono volutamente semplici e non tecniche.",
        "> **Eseguibile ora?** considera sia le dipendenze non ancora completate sia gli eventuali prerequisiti manuali registrati.",
        "",
        "| # | Prompt | PROMPT_ID | Stato | Progetto | Chat Codex | Dipendenze | Eseguibile ora? | Spiegazione | Modello | Reasoning | Tipo |",
        "| --: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for i, r in enumerate(pending, 1):
        deps = conn.execute(
            "SELECT d.depends_on_prompt_id,p.title,p.status FROM dependencies d JOIN prompts p ON p.prompt_id=d.depends_on_prompt_id "
            "WHERE d.prompt_id=? AND p.status<>'completed' ORDER BY d.depends_on_prompt_id", (r["prompt_id"],)
        ).fetchall()
        dep_text = ", ".join(_table_wikilink(f"obsidian/Prompts/{d[0]} {prompt_row(conn,d[0])['slug']}", d[0]) for d in deps) or "—"
        spieg.append(
            "| " + " | ".join([
                str(i),
                _table_wikilink(r["current_path"][:-3], r["title"]) if r["current_path"].endswith(".md") else _table_wikilink(f"obsidian/Prompts/{r['prompt_id']} {r['slug']}", f"{r['prompt_id']} · {r['title']}"),
                r["prompt_id"], r["status"], _fmt(r["project_name"] or r["project_id"]),
                _fmt(r["chat_guidance"]), dep_text, _runnable_now_text(conn, r, deps), _fmt(r["explanation"]),
                _fmt(r["model"]), _fmt(r["reasoning"]), _fmt(r["prompt_type"])
            ]) + " |"
        )
    if not pending:
        spieg.append("| — | — | — | — | — | — | — | — | Nessun prompt pendente | — | — | — |")
    spieg.append("")
    (repo/"spiegazioni.md").write_text("\n".join(spieg), encoding="utf-8")

    registry = [
        "# Prompt registry",
        "",
        "> Vista completa generata da `roadmap.sqlite`.",
        "",
        "| Prompt | Stato | Primo lancio | Ultimo lancio | Ultimo esito | Analizzato | Codice ChatGPT | Fix | Progetto | Modello | Reasoning |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        fix="—"
        if r["fix_prompt_id"]:
            fp=prompt_row(conn,r["fix_prompt_id"])
            fix=_table_wikilink(f"obsidian/Prompts/{fp['prompt_id']} {fp['slug']}", fp["prompt_id"])
        registry.append("| " + " | ".join([
            _table_wikilink(f"obsidian/Prompts/{r['prompt_id']} {r['slug']}", f"{r['prompt_id']} · {r['title']}"), r["status"], _fmt(r["first_launched_at"]), _fmt(r["last_launched_at"]),
            _fmt(_effective_outcome(r)), "sì" if r["analyzed"] else "no",
            "sì" if r["chatgpt_code_changed"] else "no", fix,
            _fmt(r["project_name"] or r["project_id"]), _fmt(r["model"]), _fmt(r["reasoning"])
        ]) + " |")
    registry.append("")
    (repo/"prompt-registry.md").write_text("\n".join(registry), encoding="utf-8")

    obs_root=repo/"obsidian"
    prompt_dir=obs_root/"Prompts"
    project_dir=obs_root/"Projects"
    dash_dir=obs_root/"Dashboards"
    for d in (prompt_dir, project_dir, dash_dir):
        d.mkdir(parents=True, exist_ok=True)

    wanted=set()
    for r in rows:
        filename=f"{r['prompt_id']} {r['slug']}.md"
        path=prompt_dir/filename
        wanted.add(path)
        deps = _prompt_links(conn, r["prompt_id"],
            "SELECT depends_on_prompt_id FROM dependencies WHERE prompt_id=? ORDER BY depends_on_prompt_id",
            (r["prompt_id"],))
        blocked = _prompt_links(conn, r["prompt_id"],
            "SELECT prompt_id FROM dependencies WHERE depends_on_prompt_id=? ORDER BY prompt_id",
            (r["prompt_id"],))
        parents = _prompt_links(conn, r["prompt_id"],
            "SELECT from_prompt_id FROM prompt_relations WHERE to_prompt_id=? AND relation_type IN ('parent','fix','followup','replacement') ORDER BY from_prompt_id",
            (r["prompt_id"],))
        children = _prompt_links(conn, r["prompt_id"],
            "SELECT to_prompt_id FROM prompt_relations WHERE from_prompt_id=? ORDER BY to_prompt_id",
            (r["prompt_id"],))
        tags=[x[0] for x in conn.execute("SELECT tag FROM prompt_tags WHERE prompt_id=? ORDER BY tag",(r["prompt_id"],)).fetchall()]
        tags += ["roadmap/prompt", f"roadmap/status/{r['status']}"]
        project_slug = re.sub(r"[^a-z0-9]+","-",(r["project_name"] or r["project_id"] or "unknown").lower()).strip("-")
        tags.append(f"roadmap/project/{project_slug or 'unknown'}")
        unique_tags=[]
        for t in tags:
            if t not in unique_tags: unique_tags.append(t)
        source_link = f"[[../../{r['current_path'][:-3]}|Apri prompt]]" if r["current_path"].endswith(".md") else "—"
        note=[
            "---",
            f"prompt_id: {r['prompt_id']}",
            f"status: {r['status']}",
            f"project_id: {_fmt(r['project_id'])}",
            f"model: {_fmt(r['model'])}",
            f"reasoning: {_fmt(r['reasoning'])}",
            "tags:",
            *[f"  - {t}" for t in unique_tags],
            "---",
            "",
            f"# {r['prompt_id']} · {r['title']}",
            "",
            f"- **Stato:** {r['status']}",
            f"- **Progetto:** [[../Projects/{project_slug or 'unknown'}|{_fmt(r['project_name'] or r['project_id'])}]]",
            f"- **Prompt:** {source_link}",
            f"- **Primo lancio:** {_fmt(r['first_launched_at'])}",
            f"- **Ultimo lancio:** {_fmt(r['last_launched_at'])}",
            f"- **Ultimo esito:** {_fmt(r['last_outcome'])}",
            f"- **Analizzato da ChatGPT:** {'sì' if r['analyzed'] else 'no'}",
            f"- **Codice modificato da ChatGPT:** {'sì' if r['chatgpt_code_changed'] else 'no'} ({r['chatgpt_code_change_count']} interventi)",
            f"- **Fix:** {_fmt(r['fix_prompt_id'])}",
            f"- **Dipende da:** {deps}",
            f"- **Sblocca:** {blocked}",
            f"- **Padri/precedenti:** {parents}",
            f"- **Figli/follow-up:** {children}",
            f"- **Chat Codex:** {_fmt(r['chat_guidance'])}",
            "",
            "## Spiegazione",
            "",
            r["explanation"] or "—",
            "",
            "## Esecuzioni",
            "",
            "| Inizio | Fine | Esito | Durata s | Modello | Reasoning | Tool-call | Token totali |",
            "| --- | --- | --- | ---: | --- | --- | ---: | ---: |",
        ]
        ex = conn.execute(
            "SELECT * FROM executions WHERE prompt_id=? ORDER BY COALESCE(started_at,ended_at,recorded_at), execution_id",
            (r["prompt_id"],)
        ).fetchall()
        for e in ex:
            note.append("| " + " | ".join([
                _fmt(e["started_at"]), _fmt(e["ended_at"]), _fmt(e["outcome"]), _fmt(e["duration_seconds"]),
                _fmt(e["model"]), _fmt(e["reasoning"]), _fmt(e["tool_call_count"]), _fmt(e["total_tokens"])
            ]) + " |")
        if not ex:
            note.append("| — | — | — | — | — | — | — | — |")
        note += ["", "## Analisi ChatGPT", ""]
        analyses=conn.execute(
            "SELECT * FROM analyses WHERE prompt_id=? ORDER BY analyzed_at,analysis_id",(r["prompt_id"],)
        ).fetchall()
        for a in analyses:
            state="sì" if a["bottlenecks_found"]==1 else ("no" if a["bottlenecks_found"]==0 else "non indicato")
            note.append(f"- {a['analyzed_at']} · colli di bottiglia: {state} · fix: {_fmt(a['fix_prompt_id'])} · {_fmt(a['summary'])}")
        if not analyses:
            note.append("- Non ancora analizzato.")
        note += ["", "## Modifiche di codice ChatGPT", ""]
        changes=conn.execute(
            "SELECT * FROM analysis_code_changes WHERE prompt_id=? ORDER BY created_at,code_change_id",
            (r["prompt_id"],)
        ).fetchall()
        for c in changes:
            commit=f" · commit `{c['commit_sha']}`" if c["commit_sha"] else ""
            note.append(
                f"- {c['created_at']} · `{c['repository']}` · {c['change_type']}{commit} · {_fmt(c['summary'])}"
            )
        if not changes:
            note.append("- Nessuna modifica di codice registrata.")
        note.append("")
        path.write_text("\n".join(note), encoding="utf-8")

    for old in prompt_dir.glob("*.md"):
        if old not in wanted:
            old.unlink()

    projects={}
    for r in rows:
        label=r["project_name"] or r["project_id"] or "Unknown"
        slug=re.sub(r"[^a-z0-9]+","-",label.lower()).strip("-") or "unknown"
        projects.setdefault((slug,label),[]).append(r)
    wanted_projects=set()
    for (slug,label),prs in projects.items():
        path=project_dir/f"{slug}.md"; wanted_projects.add(path)
        lines=["---","tags:","  - roadmap/project","---","",f"# {label}",""]
        for r in prs:
            lines.append(f"- {_wikilink_for_prompt(r)} · `{r['status']}`")
        lines.append("")
        path.write_text("\n".join(lines),encoding="utf-8")
    for old in project_dir.glob("*.md"):
        if old not in wanted_projects:
            old.unlink()

    runnable=list(conn.execute("SELECT * FROM v_runnable_prompts"))
    attention=list(conn.execute("SELECT * FROM v_attention ORDER BY updated_at DESC,prompt_id"))
    dash=[
        "# Roadmap dashboard","",
        "[[../../roadmap|Coda]] · [[../../prompt-registry|Registro completo]] · [[Attention|Da controllare]]","",
        "## Lanciabili adesso","",
    ]
    dash += [f"- {_wikilink_for_prompt(r)}" for r in runnable] or ["- Nessuno."]
    dash += ["","## In esecuzione",""]
    running=[r for r in rows if r["status"]=="running"]
    dash += [f"- {_wikilink_for_prompt(r)}" for r in running] or ["- Nessuno."]
    dash.append("")
    (dash_dir/"Roadmap.md").write_text("\n".join(dash),encoding="utf-8")

    att=["# Da controllare",""]
    att += [f"- {_wikilink_for_prompt(r)} · `{r['status']}` · analizzato={'sì' if r['analyzed'] else 'no'} · fix={_fmt(r['fix_prompt_id'])}" for r in attention] or ["- Nulla da controllare."]
    att.append("")
    (dash_dir/"Attention.md").write_text("\n".join(att),encoding="utf-8")

    conn.close()
    return ["roadmap.md","spiegazioni.md","prompt-registry.md","obsidian/"]
