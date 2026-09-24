PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prompts (
  prompt_id TEXT PRIMARY KEY CHECK (prompt_id GLOB '[0-9][0-9][0-9][0-9][0-9][0-9]'),
  slug TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  project_id TEXT,
  project_name TEXT,
  repo TEXT,
  chat_guidance TEXT,
  prompt_type TEXT NOT NULL DEFAULT 'Prompt',
  model TEXT,
  reasoning TEXT,
  megavault_mode TEXT,
  campaign_id TEXT,
  explanation TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending','running','completed','failed','blocked','cancelled','superseded','unknown')),
  queue_position INTEGER,
  current_path TEXT NOT NULL,
  materialization_sha256 TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prompt_materializations (
  prompt_id TEXT PRIMARY KEY REFERENCES prompts(prompt_id) ON DELETE CASCADE,
  body TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  created_at TEXT NOT NULL,
  actor TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dependencies (
  prompt_id TEXT NOT NULL REFERENCES prompts(prompt_id) ON DELETE CASCADE,
  depends_on_prompt_id TEXT NOT NULL REFERENCES prompts(prompt_id) ON DELETE RESTRICT,
  note TEXT,
  PRIMARY KEY (prompt_id, depends_on_prompt_id),
  CHECK (prompt_id <> depends_on_prompt_id)
);

CREATE TABLE IF NOT EXISTS prompt_relations (
  from_prompt_id TEXT NOT NULL REFERENCES prompts(prompt_id) ON DELETE CASCADE,
  to_prompt_id TEXT NOT NULL REFERENCES prompts(prompt_id) ON DELETE CASCADE,
  relation_type TEXT NOT NULL
    CHECK (relation_type IN ('fix','followup','replacement','split','merge','parent','related')),
  created_at TEXT NOT NULL,
  actor TEXT NOT NULL,
  note TEXT,
  PRIMARY KEY (from_prompt_id, to_prompt_id, relation_type)
);

CREATE TABLE IF NOT EXISTS prompt_tags (
  prompt_id TEXT NOT NULL REFERENCES prompts(prompt_id) ON DELETE CASCADE,
  tag TEXT NOT NULL,
  PRIMARY KEY (prompt_id, tag)
);

CREATE TABLE IF NOT EXISTS executions (
  execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
  prompt_id TEXT NOT NULL REFERENCES prompts(prompt_id) ON DELETE CASCADE,
  cycle_key TEXT UNIQUE,
  materialization_sha256 TEXT,
  started_at TEXT,
  ended_at TEXT,
  outcome TEXT CHECK (outcome IN ('PASS','FAIL','BLOCKED','CANCELLED','UNKNOWN')),
  duration_seconds REAL,
  model TEXT,
  reasoning TEXT,
  codex_project TEXT,
  chat_title TEXT,
  branch TEXT,
  commit_before TEXT,
  commit_after TEXT,
  tool_call_count INTEGER,
  input_tokens INTEGER,
  cached_input_tokens INTEGER,
  uncached_input_tokens INTEGER,
  output_tokens INTEGER,
  reasoning_output_tokens INTEGER,
  total_tokens INTEGER,
  source TEXT NOT NULL DEFAULT 'manual',
  recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analyses (
  analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
  prompt_id TEXT NOT NULL REFERENCES prompts(prompt_id) ON DELETE CASCADE,
  analyzed_at TEXT NOT NULL,
  actor TEXT NOT NULL DEFAULT 'chatgpt',
  bottlenecks_found INTEGER CHECK (bottlenecks_found IN (0,1) OR bottlenecks_found IS NULL),
  summary TEXT,
  fix_prompt_id TEXT REFERENCES prompts(prompt_id) ON DELETE SET NULL,
  source_ref TEXT
);

CREATE TABLE IF NOT EXISTS analysis_code_changes (
  code_change_id INTEGER PRIMARY KEY AUTOINCREMENT,
  analysis_id INTEGER NOT NULL REFERENCES analyses(analysis_id) ON DELETE CASCADE,
  prompt_id TEXT NOT NULL REFERENCES prompts(prompt_id) ON DELETE CASCADE,
  repository TEXT NOT NULL,
  change_type TEXT NOT NULL,
  commit_sha TEXT,
  summary TEXT,
  created_at TEXT NOT NULL,
  actor TEXT NOT NULL DEFAULT 'chatgpt'
);

CREATE TABLE IF NOT EXISTS artifacts (
  artifact_id INTEGER PRIMARY KEY AUTOINCREMENT,
  prompt_id TEXT NOT NULL REFERENCES prompts(prompt_id) ON DELETE CASCADE,
  artifact_type TEXT NOT NULL,
  uri TEXT NOT NULL,
  label TEXT,
  created_at TEXT NOT NULL,
  UNIQUE(prompt_id, artifact_type, uri)
);

CREATE TABLE IF NOT EXISTS status_history (
  history_id INTEGER PRIMARY KEY AUTOINCREMENT,
  prompt_id TEXT NOT NULL REFERENCES prompts(prompt_id) ON DELETE CASCADE,
  old_status TEXT,
  new_status TEXT NOT NULL,
  changed_at TEXT NOT NULL,
  actor TEXT NOT NULL,
  note TEXT
);

CREATE TABLE IF NOT EXISTS identity_conflicts (
  conflict_id INTEGER PRIMARY KEY AUTOINCREMENT,
  prompt_id TEXT NOT NULL,
  observed_cycle_key TEXT,
  expected_sha256 TEXT,
  observed_sha256 TEXT NOT NULL,
  detected_at TEXT NOT NULL,
  source TEXT NOT NULL,
  UNIQUE(prompt_id, observed_cycle_key, observed_sha256)
);

CREATE TABLE IF NOT EXISTS audit_events (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  prompt_id TEXT REFERENCES prompts(prompt_id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  event_at TEXT NOT NULL,
  actor TEXT NOT NULL,
  payload_json TEXT
);

CREATE TABLE IF NOT EXISTS mutation_receipts (
  request_key TEXT PRIMARY KEY,
  issue_number INTEGER NOT NULL UNIQUE,
  payload_sha256 TEXT NOT NULL,
  actor TEXT NOT NULL,
  applied_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_prompts_status_queue ON prompts(status, queue_position);
CREATE INDEX IF NOT EXISTS idx_executions_prompt_time ON executions(prompt_id, started_at, ended_at);
CREATE INDEX IF NOT EXISTS idx_analyses_prompt_time ON analyses(prompt_id, analyzed_at);
CREATE INDEX IF NOT EXISTS idx_code_changes_prompt_time ON analysis_code_changes(prompt_id, created_at);

DROP VIEW IF EXISTS v_attention;
DROP VIEW IF EXISTS v_pbf_dispositions;
DROP VIEW IF EXISTS v_runnable_prompts;
DROP VIEW IF EXISTS v_prompt_summary;

CREATE VIEW v_prompt_summary AS
SELECT
  p.*,
  (SELECT MIN(e.started_at) FROM executions e WHERE e.prompt_id=p.prompt_id) AS first_launched_at,
  (SELECT MAX(e.started_at) FROM executions e WHERE e.prompt_id=p.prompt_id) AS last_launched_at,
  (SELECT e.outcome FROM executions e WHERE e.prompt_id=p.prompt_id
     ORDER BY COALESCE(e.ended_at,e.started_at,e.recorded_at) DESC, e.execution_id DESC LIMIT 1) AS last_outcome,
  EXISTS(SELECT 1 FROM analyses a WHERE a.prompt_id=p.prompt_id) AS analyzed,
  EXISTS(SELECT 1 FROM analysis_code_changes c WHERE c.prompt_id=p.prompt_id) AS chatgpt_code_changed,
  (SELECT COUNT(*) FROM analysis_code_changes c WHERE c.prompt_id=p.prompt_id) AS chatgpt_code_change_count,
  (SELECT a.bottlenecks_found FROM analyses a WHERE a.prompt_id=p.prompt_id
     ORDER BY a.analyzed_at DESC, a.analysis_id DESC LIMIT 1) AS bottlenecks_found,
  (SELECT a.fix_prompt_id FROM analyses a WHERE a.prompt_id=p.prompt_id AND a.fix_prompt_id IS NOT NULL
     ORDER BY a.analyzed_at DESC, a.analysis_id DESC LIMIT 1) AS fix_prompt_id
FROM prompts p;

CREATE VIEW v_runnable_prompts AS
SELECT p.*
FROM prompts p
WHERE p.status='pending'
  AND NOT EXISTS (
    SELECT 1
    FROM dependencies d
    JOIN prompts dep ON dep.prompt_id=d.depends_on_prompt_id
    WHERE d.prompt_id=p.prompt_id AND dep.status<>'completed'
  )
  AND NOT EXISTS (
    SELECT 1
    FROM prompt_tags t
    WHERE t.prompt_id=p.prompt_id
      AND t.tag LIKE 'manual-prerequisite:%'
  )
ORDER BY COALESCE(p.queue_position, 2147483647), p.created_at, p.prompt_id;

CREATE VIEW v_pbf_dispositions AS
WITH RECURSIVE
pbf_base AS (
  SELECT s.*
  FROM v_prompt_summary s
  WHERE s.status IN ('failed','blocked','unknown','cancelled','superseded')
     OR EXISTS (
       SELECT 1
       FROM executions e
       WHERE e.prompt_id=s.prompt_id
         AND e.outcome IN ('FAIL','BLOCKED','UNKNOWN','CANCELLED')
     )
),
relation_walk(source_prompt_id,current_prompt_id,depth,path,via_resolved_by) AS (
  SELECT
    r.from_prompt_id,
    r.to_prompt_id,
    1,
    '|' || r.from_prompt_id || '|' || r.to_prompt_id || '|',
    CASE WHEN r.relation_type='resolved_by' THEN 1 ELSE 0 END
  FROM prompt_relations r
  JOIN pbf_base b ON b.prompt_id=r.from_prompt_id
  WHERE r.relation_type IN ('fix','replacement','followup','merge','resolved_by')
  UNION ALL
  SELECT
    w.source_prompt_id,
    r.to_prompt_id,
    w.depth+1,
    w.path || r.to_prompt_id || '|',
    CASE WHEN w.via_resolved_by=1 OR r.relation_type='resolved_by' THEN 1 ELSE 0 END
  FROM relation_walk w
  JOIN prompt_relations r ON r.from_prompt_id=w.current_prompt_id
  WHERE r.relation_type IN ('fix','replacement','followup','merge','resolved_by')
    AND w.depth < 16
    AND instr(w.path, '|' || r.to_prompt_id || '|')=0
),
signals AS (
  SELECT
    b.prompt_id,
    EXISTS (
      SELECT 1
      FROM relation_walk w
      JOIN prompts successor ON successor.prompt_id=w.current_prompt_id
      WHERE w.source_prompt_id=b.prompt_id
        AND successor.status='completed'
        AND w.via_resolved_by=1
    ) AS resolved_by_completed,
    EXISTS (
      SELECT 1
      FROM relation_walk w
      JOIN prompts successor ON successor.prompt_id=w.current_prompt_id
      WHERE w.source_prompt_id=b.prompt_id
        AND successor.status IN ('pending','running','completed')
    ) AS has_live_or_completed_successor,
    EXISTS (
      SELECT 1
      FROM prompt_relations r
      WHERE r.from_prompt_id=b.prompt_id
        AND r.relation_type='replacement'
    ) AS has_replacement,
    EXISTS (
      SELECT 1
      FROM status_history sh
      WHERE sh.prompt_id=b.prompt_id
        AND sh.old_status IS NOT NULL
        AND sh.new_status IN ('cancelled','superseded')
        AND trim(COALESCE(sh.note,''))<>''
    ) AS has_terminal_reason,
    (
      COALESCE(b.current_path,'')=''
      AND b.project_id IS NULL
      AND COALESCE(b.project_name,'')=''
      AND COALESCE(b.repo,'')=''
      AND NOT EXISTS (
        SELECT 1 FROM prompt_materializations pm WHERE pm.prompt_id=b.prompt_id
      )
    ) AS historical_stub
  FROM pbf_base b
)
SELECT
  b.*,
  CASE
    WHEN s.historical_stub THEN 'historical_unclassified'
    WHEN b.status='completed' THEN 'resolved'
    WHEN s.resolved_by_completed THEN 'resolved'
    WHEN s.has_live_or_completed_successor THEN 'covered'
    WHEN b.status IN ('cancelled','superseded')
         AND (s.has_terminal_reason OR s.has_replacement) THEN 'waived'
    ELSE 'needs_fix'
  END AS pbf_disposition
FROM pbf_base b
JOIN signals s ON s.prompt_id=b.prompt_id;

CREATE VIEW v_attention AS
SELECT s.*
FROM v_prompt_summary s
JOIN v_pbf_dispositions pbf ON pbf.prompt_id=s.prompt_id
WHERE pbf.pbf_disposition='needs_fix';
