"""Event bus — bus d'événements SQLite pour la communication inter-agents.

Les agents continuent d'écrire leurs fichiers JSON dans ~/.openclaw/shared/
(rétrocompatibilité), mais POSTENT aussi un événement sur ce bus.
Les consommateurs lisent les événements auxquels ils sont abonnés.

Usage:
  from polis.eventbus import EventBus
  bus = EventBus()
  bus.post_event("health.updated", "defenseur", payload={...})
  events = bus.get_events(target="intendant")
"""

import json
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path.home() / ".openclaw" / "events.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS events (
  id     INTEGER PRIMARY KEY AUTOINCREMENT,
  event_type TEXT  NOT NULL,
  source   TEXT  NOT NULL,
  targets   TEXT,       -- NULL = broadcast, sinon JSON array
  payload   TEXT  NOT NULL, -- JSON
  status   TEXT  NOT NULL DEFAULT 'pending', -- pending | delivered | acknowledged
  created_at TEXT  NOT NULL,
  delivered_at TEXT,
  acked_at  TEXT
);

CREATE INDEX IF NOT EXISTS idx_events_targets ON events(targets);
CREATE INDEX IF NOT EXISTS idx_events_source ON events(source);
CREATE INDEX IF NOT EXISTS idx_events_status ON events(status);
CREATE INDEX IF NOT EXISTS idx_events_created ON events(created_at);
"""


class EventBusError(Exception):
  """Erreur du bus d'événements."""


class EventBus:
  """Bus d'événements SQLite pour la communication inter-agents."""

  def __init__(self, db_path: Path | None = None):
    self.db_path = db_path or DEFAULT_DB_PATH
    self._ensure_dir()
    self.init_db()

  def _ensure_dir(self) -> None:
    self.db_path.parent.mkdir(parents=True, exist_ok=True)

  def init_db(self) -> None:
    """Crée la base si elle n'existe pas."""
    with self._connect() as conn:
      conn.executescript(SCHEMA_SQL)

  def _connect(self) -> sqlite3.Connection:
    """Retourne une connexion SQLite (context manager)."""
    conn = sqlite3.connect(str(self.db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

  def post_event(
    self,
    event_type: str,
    source: str,
    payload: dict,
    targets: list[str] | None = None,
  ) -> int:
    """Poste un événement sur le bus. Retourne l'ID."""
    now = datetime.now(UTC).isoformat()
    targets_json = json.dumps(targets) if targets else None
    payload_json = json.dumps(payload, ensure_ascii=False)

    with self._connect() as conn:
      cur = conn.execute(
        """INSERT INTO events (event_type, source, targets, payload, status, created_at)
          VALUES (?, ?, ?, ?, 'pending', ?)""",
        (event_type, source, targets_json, payload_json, now),
      )
      assert cur.lastrowid is not None
      return cur.lastrowid

  def get_events(
    self,
    target: str | None = None,
    source: str | None = None,
    event_type: str | None = None,
    status: str | None = None,
    limit: int = 50,
    since: str | None = None,
  ) -> list[dict[str, Any]]:
    """Lit les événements du bus avec filtres optionnels."""
    clauses = ["1=1"]
    params: list[str | int] = []

    if target:
      clauses.append("(targets IS NULL OR targets LIKE ?)")
      params.append(f"%{target}%")
    if source:
      clauses.append("source = ?")
      params.append(source)
    if event_type:
      clauses.append("event_type = ?")
      params.append(event_type)
    if status:
      clauses.append("status = ?")
      params.append(status)
    if since:
      clauses.append("created_at >= ?")
      params.append(since)

    query = ( # noqa: S608
      "SELECT id, event_type, source, targets, payload, status, "
      "created_at, delivered_at, acked_at "
      "FROM events "
      f"WHERE {' AND '.join(clauses)} " # noqa: S608
      "ORDER BY created_at DESC LIMIT ?"
    )
    params.append(limit)

    with self._connect() as conn:
      rows = conn.execute(query, params).fetchall()

    results = []
    for row in rows:
      ev = dict(row)
      ev["payload"] = json.loads(ev["payload"])
      if ev["targets"]:
        ev["targets"] = json.loads(ev["targets"])
      results.append(ev)
    return results

  def ack_event(self, event_id: int) -> bool:
    """Marque un événement comme acquitté."""
    now = datetime.now(UTC).isoformat()
    with self._connect() as conn:
      cur = conn.execute(
        "UPDATE events SET status = 'acknowledged', acked_at = ? WHERE id = ?",
        (now, event_id),
      )
      return bool(cur.rowcount)

  def mark_delivered(self, event_id: int) -> bool:
    """Marque un événement comme délivré."""
    now = datetime.now(UTC).isoformat()
    with self._connect() as conn:
      cur = conn.execute(
        "UPDATE events SET status = 'delivered', delivered_at = ? WHERE id = ?",
        (now, event_id),
      )
      return bool(cur.rowcount)

  def purge(self, before: datetime | None = None) -> int:
    """Supprime les événements antérieurs à `before` (défaut: 7 jours)."""
    if before is None:
      before = datetime.now(UTC) - timedelta(days=7)
    cutoff = before.isoformat()
    with self._connect() as conn:
      cur = conn.execute("DELETE FROM events WHERE created_at < ?", (cutoff,))
      return cur.rowcount

  def status(self) -> dict[str, Any]:
    """Retourne des statistiques sur le bus."""
    with self._connect() as conn:
      total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
      by_type = {
        r["event_type"]: r["cnt"]
        for r in conn.execute(
          "SELECT event_type, COUNT(*) as cnt FROM events GROUP BY event_type"
        ).fetchall()
      }
      by_source = {
        r["source"]: r["cnt"]
        for r in conn.execute(
          "SELECT source, COUNT(*) as cnt FROM events GROUP BY source"
        ).fetchall()
      }
      by_status = {
        r["status"]: r["cnt"]
        for r in conn.execute(
          "SELECT status, COUNT(*) as cnt FROM events GROUP BY status"
        ).fetchall()
      }
      oldest = conn.execute("SELECT MIN(created_at) FROM events").fetchone()[0]
      newest = conn.execute("SELECT MAX(created_at) FROM events").fetchone()[0]
    return {
      "total": total,
      "by_type": by_type,
      "by_source": by_source,
      "by_status": by_status,
      "oldest_event": oldest,
      "newest_event": newest,
      "db_path": str(self.db_path),
    }
