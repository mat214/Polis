"""Rate limiting — sliding window avec SQLite.

Limites par défaut :
 READ      : illimité
 WRITE      : 30/min, 200/h
 WRITE_SENSITIVE : 3/min, 20/h
 IRREVERSIBLE  : 1/min, 5/h
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

DB_PATH = Path.home() / ".openclaw" / "guardrail_rates.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS requests (
  id      INTEGER PRIMARY KEY AUTOINCREMENT,
  agent     TEXT NOT NULL,
  skill     TEXT NOT NULL,
  action    TEXT NOT NULL,
  level     INTEGER NOT NULL,
  requested_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_rates_lookup
  ON requests(agent, skill, action, level, requested_at);
CREATE INDEX IF NOT EXISTS idx_rates_cleanup
  ON requests(requested_at);
"""

# Limites : (label, per_minute, per_hour)
LIMITS = {
  0: (None, None), # READ — illimité
  1: (30, 200), # WRITE
  2: (3, 20), # WRITE_SENSITIVE
  3: (1, 5), # IRREVERSIBLE
}


class RateLimitExceeded(Exception):
  """Dépassement de rate limit."""


def _init_db() -> None:
  DB_PATH.parent.mkdir(parents=True, exist_ok=True)
  with sqlite3.connect(str(DB_PATH)) as conn:
    conn.executescript(SCHEMA)


def _cleanup() -> None:
  """Nettoie les entrées plus vieilles que 1 heure."""
  cutoff = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
  with sqlite3.connect(str(DB_PATH)) as conn:
    conn.execute("DELETE FROM requests WHERE requested_at < ?", (cutoff,))


def _count(agent: str, skill: str, action: str, level: int, since: datetime) -> int:
  """Compte les requêtes pour (agent, skill, action, level) depuis `since`."""
  with sqlite3.connect(str(DB_PATH)) as conn:
    row = conn.execute(
      "SELECT COUNT(*) FROM requests "
      "WHERE agent = ? AND skill = ? AND action = ? AND level = ? AND requested_at >= ?",
      (agent, skill, action, level, since.isoformat()),
    ).fetchone()
    return row[0] if row else 0


def check(agent: str, skill: str, action: str, level: int) -> None:
  """Vérifie les rate limits. Lève RateLimitExceeded si dépassé."""
  _init_db()

  now = datetime.now(UTC)
  limits = LIMITS.get(level)

  if limits is None or limits == (None, None):
    return

  max_min, max_hour = limits

  if max_min is not None:
    count_min = _count(agent, skill, action, level, now - timedelta(minutes=1))
    if count_min >= max_min:
      raise RateLimitExceeded(
        f"Rate limit minute dépassé pour {agent}/{skill}/{action} "
        f"(N{level}) : {count_min}/{max_min} par minute"
      )

  if max_hour is not None:
    count_hour = _count(agent, skill, action, level, now - timedelta(hours=1))
    if count_hour >= max_hour:
      raise RateLimitExceeded(
        f"Rate limit heure dépassé pour {agent}/{skill}/{action} "
        f"(N{level}) : {count_hour}/{max_hour} par heure"
      )

  # Enregistrer la requête
  with sqlite3.connect(str(DB_PATH)) as conn:
    conn.execute(
      "INSERT INTO requests (agent, skill, action, level, requested_at) VALUES (?, ?, ?, ?, ?)",
      (agent, skill, action, level, now.isoformat()),
    )

  # Nettoyage opportuniste (1 appel sur ~50)
  if _count(agent, skill, action, level, now - timedelta(hours=1)) == 1:
    _cleanup()
