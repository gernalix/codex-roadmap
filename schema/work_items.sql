CREATE TABLE IF NOT EXISTS work_items (
  work_item_id TEXT PRIMARY KEY,
  parent_id TEXT REFERENCES work_items(work_item_id) ON DELETE RESTRICT,
  kind TEXT NOT NULL CHECK (kind IN ('goal','task','phase','step','gate')),
  title TEXT NOT NULL,
  status TEXT NOT NULL CHECK (
    status IN (
      'pending','running','waiting','completed','failed','blocked',
      'cancelled','superseded','waived','needs_fix','unknown'
    )
  ),
  executor_policy TEXT NOT NULL DEFAULT 'auto'
    CHECK (executor_policy IN ('auto','codex','rdc','chatgpt','human')),
  sort_order INTEGER,
  current_action TEXT,
  next_action TEXT,
  blocker TEXT,
  project_id TEXT,
  project_name TEXT,
  repo TEXT,
  prompt_id TEXT UNIQUE,
  task_id TEXT UNIQUE,
  required INTEGER NOT NULL DEFAULT 1 CHECK (required IN (0,1)),
  actionable INTEGER NOT NULL DEFAULT 1 CHECK (actionable IN (0,1)),
  source_kind TEXT NOT NULL DEFAULT 'manual',
  source_ref TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS work_item_dependencies (
  work_item_id TEXT NOT NULL REFERENCES work_items(work_item_id) ON DELETE CASCADE,
  depends_on_work_item_id TEXT NOT NULL REFERENCES work_items(work_item_id) ON DELETE RESTRICT,
  required INTEGER NOT NULL DEFAULT 1 CHECK (required IN (0,1)),
  note TEXT,
  PRIMARY KEY (work_item_id, depends_on_work_item_id),
  CHECK (work_item_id <> depends_on_work_item_id)
);

CREATE TABLE IF NOT EXISTS work_item_relations (
  from_work_item_id TEXT NOT NULL REFERENCES work_items(work_item_id) ON DELETE CASCADE,
  to_work_item_id TEXT NOT NULL REFERENCES work_items(work_item_id) ON DELETE CASCADE,
  relation_type TEXT NOT NULL,
  created_at TEXT NOT NULL,
  actor TEXT NOT NULL,
  note TEXT,
  PRIMARY KEY (from_work_item_id, to_work_item_id, relation_type)
);

CREATE TABLE IF NOT EXISTS work_item_tags (
  work_item_id TEXT NOT NULL REFERENCES work_items(work_item_id) ON DELETE CASCADE,
  tag TEXT NOT NULL,
  PRIMARY KEY (work_item_id, tag)
);
CREATE TABLE IF NOT EXISTS work_item_checkpoints (
  checkpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
  work_item_id TEXT NOT NULL REFERENCES work_items(work_item_id) ON DELETE CASCADE,
  source_file TEXT,
  source_commit TEXT,
  source_sha256 TEXT NOT NULL,
  objective TEXT,
  current_step TEXT,
  next_action TEXT,
  blocker TEXT,
  completed_json TEXT,
  remaining_json TEXT,
  evidence_json TEXT,
  captured_at TEXT NOT NULL,
  UNIQUE(work_item_id, source_file, source_sha256)
);

CREATE TABLE IF NOT EXISTS work_item_evidence (
  evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
  work_item_id TEXT NOT NULL REFERENCES work_items(work_item_id) ON DELETE CASCADE,
  evidence_kind TEXT NOT NULL,
  label TEXT,
  uri TEXT,
  value_json TEXT,
  created_at TEXT NOT NULL,
  UNIQUE(work_item_id, evidence_kind, uri, label)
);

CREATE INDEX IF NOT EXISTS idx_work_items_parent_order
  ON work_items(parent_id, sort_order, work_item_id);
CREATE INDEX IF NOT EXISTS idx_work_items_status_order
  ON work_items(status, sort_order, work_item_id);
CREATE INDEX IF NOT EXISTS idx_work_items_prompt_id
  ON work_items(prompt_id);
CREATE INDEX IF NOT EXISTS idx_work_item_dependencies_target
  ON work_item_dependencies(depends_on_work_item_id, work_item_id);

DROP VIEW IF EXISTS v_work_item_runnable;
DROP VIEW IF EXISTS v_work_item_summary;
DROP VIEW IF EXISTS v_work_item_progress;
CREATE VIEW v_work_item_progress AS
WITH RECURSIVE descendants(root_id, work_item_id) AS (
  SELECT parent.work_item_id, child.work_item_id
  FROM work_items parent
  JOIN work_items child ON child.parent_id=parent.work_item_id
  UNION ALL
  SELECT d.root_id, child.work_item_id
  FROM descendants d
  JOIN work_items child ON child.parent_id=d.work_item_id
),
stats AS (
  SELECT
    d.root_id,
    SUM(CASE WHEN child.actionable=1 THEN 1 ELSE 0 END) AS total_actionable,
    SUM(
      CASE
        WHEN child.actionable=1
         AND child.status IN ('completed','waived','cancelled','superseded')
        THEN 1 ELSE 0
      END
    ) AS completed_actionable
  FROM descendants d
  JOIN work_items child ON child.work_item_id=d.work_item_id
  GROUP BY d.root_id
)
SELECT
  w.work_item_id,
  CASE
    WHEN COALESCE(s.total_actionable,0)>0 THEN s.total_actionable
    WHEN w.actionable=1 THEN 1 ELSE 0
  END AS total_actionable,
  CASE
    WHEN COALESCE(s.total_actionable,0)>0 THEN COALESCE(s.completed_actionable,0)
    WHEN w.actionable=1
     AND w.status IN ('completed','waived','cancelled','superseded')
    THEN 1 ELSE 0
  END AS completed_actionable,
  CASE
    WHEN (
      CASE
        WHEN COALESCE(s.total_actionable,0)>0 THEN s.total_actionable
        WHEN w.actionable=1 THEN 1 ELSE 0
      END
    )=0 THEN 100.0
    ELSE ROUND(
      100.0 * (
        CASE
          WHEN COALESCE(s.total_actionable,0)>0 THEN COALESCE(s.completed_actionable,0)
          WHEN w.actionable=1
           AND w.status IN ('completed','waived','cancelled','superseded')
          THEN 1 ELSE 0
        END
      ) / (
        CASE
          WHEN COALESCE(s.total_actionable,0)>0 THEN s.total_actionable
          WHEN w.actionable=1 THEN 1 ELSE 1
        END
      ),
      1
    )
  END AS progress_percent
FROM work_items w
LEFT JOIN stats s ON s.root_id=w.work_item_id;

CREATE VIEW v_work_item_summary AS
SELECT w.*, p.total_actionable, p.completed_actionable, p.progress_percent
FROM work_items w
JOIN v_work_item_progress p ON p.work_item_id=w.work_item_id;

CREATE VIEW v_work_item_runnable AS
SELECT w.*
FROM work_items w
WHERE w.status='pending'
  AND w.actionable=1
  AND w.executor_policy<>'human'
  AND NOT EXISTS (
    SELECT 1
    FROM work_item_dependencies d
    JOIN work_items dep ON dep.work_item_id=d.depends_on_work_item_id
    WHERE d.work_item_id=w.work_item_id
      AND d.required=1
      AND dep.status NOT IN ('completed','waived','cancelled','superseded')
  )
  AND NOT EXISTS (
    SELECT 1 FROM work_item_tags t
    WHERE t.work_item_id=w.work_item_id
      AND t.tag LIKE 'manual-prerequisite:%'
  )
ORDER BY COALESCE(w.sort_order,2147483647), w.created_at, w.work_item_id;


-- C2-owned project/repository identity and PROMPT_ID registry imported once from MegaVault.
CREATE TABLE IF NOT EXISTS projects (
  project_id INTEGER PRIMARY KEY,
  slug TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  status TEXT NOT NULL,
  archived INTEGER NOT NULL DEFAULT 0 CHECK(archived IN (0,1)),
  created_source TEXT NOT NULL,
  notes TEXT
);
CREATE TABLE IF NOT EXISTS project_aliases (
  alias TEXT PRIMARY KEY,
  project_id INTEGER NOT NULL REFERENCES projects(project_id) ON UPDATE CASCADE ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS repositories (
  repository_id TEXT PRIMARY KEY,
  project_id INTEGER NOT NULL REFERENCES projects(project_id) ON UPDATE CASCADE ON DELETE RESTRICT,
  location TEXT NOT NULL,
  kind TEXT NOT NULL,
  branch TEXT,
  head TEXT,
  status TEXT,
  canonical INTEGER NOT NULL DEFAULT 1 CHECK(canonical IN (0,1)),
  repository_kind TEXT,
  host_id TEXT,
  worktree_path TEXT,
  remote_url TEXT,
  runtime_path TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_repositories_one_canonical_worktree
  ON repositories(project_id) WHERE repository_kind='local_worktree' AND canonical=1;
CREATE INDEX IF NOT EXISTS idx_repositories_project_kind
  ON repositories(project_id,repository_kind,canonical,repository_id);
CREATE TABLE IF NOT EXISTS project_components (
  component_id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(project_id) ON UPDATE CASCADE ON DELETE RESTRICT,
  component TEXT NOT NULL,
  type TEXT NOT NULL,
  path TEXT NOT NULL,
  purpose TEXT NOT NULL,
  UNIQUE(project_id,component)
);
CREATE INDEX IF NOT EXISTS idx_project_components_project
  ON project_components(project_id,type,component);
CREATE TABLE IF NOT EXISTS project_operations (
  operation_id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(project_id) ON UPDATE CASCADE ON DELETE RESTRICT,
  operation TEXT NOT NULL,
  command TEXT NOT NULL,
  scope TEXT NOT NULL,
  host TEXT,
  workdir TEXT,
  risk_level TEXT NOT NULL CHECK(risk_level IN ('low','medium','high')),
  notes TEXT,
  UNIQUE(project_id,operation)
);
CREATE INDEX IF NOT EXISTS idx_project_operations_project
  ON project_operations(project_id,risk_level,operation);

CREATE TABLE IF NOT EXISTS prompt_id_registry (
  prompt_id INTEGER PRIMARY KEY CHECK (prompt_id BETWEEN 100000 AND 999999),
  parent_prompt_id INTEGER
    REFERENCES prompt_id_registry(prompt_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  project_id INTEGER
    REFERENCES projects(project_id)
    ON UPDATE CASCADE ON DELETE SET NULL,
  source TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'allocated'
    CHECK (status IN ('allocated','materialized','used','cancelled')),
  content_sha256 TEXT
    CHECK (
      content_sha256 IS NULL OR (
        length(content_sha256)=64
        AND content_sha256 NOT GLOB '*[^0-9a-f]*'
      )
    ),
  created_at_utc TEXT NOT NULL,
  materialized_at_utc TEXT,
  used_at_utc TEXT,
  cancelled_at_utc TEXT,
  CHECK (parent_prompt_id IS NULL OR parent_prompt_id <> prompt_id),
  CHECK (
    (status='allocated' AND content_sha256 IS NULL
      AND materialized_at_utc IS NULL AND used_at_utc IS NULL AND cancelled_at_utc IS NULL)
    OR
    (status='materialized' AND content_sha256 IS NOT NULL
      AND materialized_at_utc IS NOT NULL AND used_at_utc IS NULL AND cancelled_at_utc IS NULL)
    OR
    (status='used' AND content_sha256 IS NOT NULL
      AND materialized_at_utc IS NOT NULL AND used_at_utc IS NOT NULL AND cancelled_at_utc IS NULL)
    OR
    (status='cancelled' AND used_at_utc IS NULL AND cancelled_at_utc IS NOT NULL
      AND ((content_sha256 IS NULL AND materialized_at_utc IS NULL)
        OR (content_sha256 IS NOT NULL AND materialized_at_utc IS NOT NULL)))
  )
);
CREATE INDEX IF NOT EXISTS idx_prompt_id_parent ON prompt_id_registry(parent_prompt_id);
CREATE INDEX IF NOT EXISTS idx_prompt_id_project_created ON prompt_id_registry(project_id,created_at_utc);
CREATE INDEX IF NOT EXISTS idx_prompt_id_status ON prompt_id_registry(status,created_at_utc);

CREATE TABLE IF NOT EXISTS prompt_id_events (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  prompt_id INTEGER NOT NULL
    REFERENCES prompt_id_registry(prompt_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  event_type TEXT NOT NULL
    CHECK (event_type IN ('allocated','materialized','used','cancelled')),
  event_at_utc TEXT NOT NULL,
  detail TEXT
);
CREATE INDEX IF NOT EXISTS idx_prompt_id_events_prompt
  ON prompt_id_events(prompt_id,event_id);

CREATE TRIGGER IF NOT EXISTS prompt_id_registry_no_delete
BEFORE DELETE ON prompt_id_registry
BEGIN
  SELECT RAISE(ABORT, 'PROMPT_ID_REUSE_FORBIDDEN');
END;

CREATE TRIGGER IF NOT EXISTS prompt_id_identity_immutable
BEFORE UPDATE OF prompt_id,parent_prompt_id,project_id,source,created_at_utc
ON prompt_id_registry
WHEN
  NEW.prompt_id IS NOT OLD.prompt_id
  OR NEW.parent_prompt_id IS NOT OLD.parent_prompt_id
  OR NEW.project_id IS NOT OLD.project_id
  OR NEW.source IS NOT OLD.source
  OR NEW.created_at_utc IS NOT OLD.created_at_utc
BEGIN
  SELECT RAISE(ABORT, 'PROMPT_ID_IDENTITY_IMMUTABLE');
END;

CREATE TRIGGER IF NOT EXISTS prompt_id_hash_immutable_after_set
BEFORE UPDATE OF content_sha256 ON prompt_id_registry
WHEN OLD.content_sha256 IS NOT NULL
  AND NEW.content_sha256 IS NOT OLD.content_sha256
BEGIN
  SELECT RAISE(ABORT, 'PROMPT_ID_CONTENT_IMMUTABLE');
END;

CREATE TRIGGER IF NOT EXISTS prompt_id_state_transition_guard
BEFORE UPDATE OF status ON prompt_id_registry
WHEN NEW.status IS NOT OLD.status
  AND NOT (
    (OLD.status='allocated' AND NEW.status IN ('materialized','cancelled'))
    OR
    (OLD.status='materialized' AND NEW.status IN ('used','cancelled'))
  )
BEGIN
  SELECT RAISE(ABORT, 'PROMPT_ID_INVALID_STATE_TRANSITION');
END;

CREATE TRIGGER IF NOT EXISTS prompt_id_events_no_update
BEFORE UPDATE ON prompt_id_events
BEGIN
  SELECT RAISE(ABORT, 'PROMPT_ID_EVENT_IMMUTABLE');
END;

CREATE TRIGGER IF NOT EXISTS prompt_id_events_no_delete
BEFORE DELETE ON prompt_id_events
BEGIN
  SELECT RAISE(ABORT, 'PROMPT_ID_EVENT_IMMUTABLE');
END;


-- Preserve allocator request replay identity across the authority migration.
CREATE TABLE IF NOT EXISTS prompt_id_allocation_requests (
  request_id TEXT PRIMARY KEY CHECK(length(request_id) BETWEEN 1 AND 180
    AND request_id NOT GLOB '*[^A-Za-z0-9._-]*'),
  prompt_id INTEGER NOT NULL UNIQUE REFERENCES prompt_id_registry(prompt_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  source TEXT NOT NULL, project_id INTEGER, parent_prompt_id INTEGER,
  created_at_utc TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
