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
