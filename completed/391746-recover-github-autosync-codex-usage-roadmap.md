PROMPT_ID=391746

# Goal
Recuperare gli alert Git autosync: `codex-usage` project_id=60 con `push_failed (ahead=1)` e `codex-roadmap` con `dirty_worktree`.

# Starting point
- `codex-usage`: `/home/daniele/projects/codex-usage`, project_id=60.
- `codex-roadmap`: `/home/daniele/projects/codex-roadmap` su `main`; aggiornare esclusivamente con `tools/roadmap_pull.py`.

# Scope
Preservare commit e modifiche locali; diagnosticare e riconciliare divergenze/conflict, committare e fare push quando necessario; non usare reset hard, clean o scritture dirette al DB/vista della roadmap. Usare il single writer e i workflow Git canonici della roadmap.

# Acceptance criteria
- `codex-usage` non è più `push_failed (ahead=1)` e il branch è sincronizzato al remoto.
- `codex-roadmap` non è più anomalo `dirty_worktree` ed è sincronizzabile con il workflow canonico.
- I due `git status -sb` finali non mostrano conflitti e sono coerenti con il remoto.
- Un controllo autosync mirato finale non riporta i due alert.
