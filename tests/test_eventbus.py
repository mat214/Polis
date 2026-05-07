"""Tests du bus d'événements SQLite (polis/eventbus.py)."""

from datetime import UTC, datetime, timedelta

import pytest

from polis.eventbus import EventBus


@pytest.fixture
def bus(tmp_path):
  """Bus d'événements avec base temporaire."""
  db_path = tmp_path / "events.db"
  eb = EventBus(db_path=db_path)
  yield eb


class TestEventBusCore:
  """Tests unitaires du module eventbus."""

  def test_init_creates_db(self, bus):
    """L'initialisation crée la base et la table events."""
    assert bus.db_path.exists()
    with bus._connect() as conn:
      tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='events'"
      ).fetchall()
      assert len(tables) == 1

  def test_post_event_returns_id(self, bus):
    """Poster un événement retourne un ID entier."""
    ev_id = bus.post_event("health.updated", "defenseur", {"status": "ok"})
    assert isinstance(ev_id, int)
    assert ev_id > 0

  def test_post_and_read_event(self, bus):
    """Un événement posté est lisible."""
    bus.post_event(
      "health.updated", "defenseur", {"status": "ok", "score": 85}, targets=["intendant"]
    )
    events = bus.get_events()
    assert len(events) == 1
    assert events[0]["event_type"] == "health.updated"
    assert events[0]["source"] == "defenseur"
    assert events[0]["payload"]["status"] == "ok"
    assert events[0]["targets"] == ["intendant"]

  def test_ack_event(self, bus):
    """Acquitter un événement change son statut."""
    ev_id = bus.post_event("alert.raised", "defenseur", {"level": "HAUT"})
    assert bus.ack_event(ev_id)
    events = bus.get_events(status="acknowledged")
    assert len(events) == 1
    assert events[0]["acked_at"] is not None

  def test_mark_delivered(self, bus):
    """Marquer un événement comme délivré."""
    ev_id = bus.post_event("task.created", "intendant", {"action": "backup"})
    assert bus.mark_delivered(ev_id)
    events = bus.get_events(status="delivered")
    assert len(events) >= 1

  def test_purge_old_events(self, bus):
    """La purge supprime les événements antérieurs à la date donnée."""
    bus.post_event("health.updated", "defenseur", {"status": "ok"})
    assert len(bus.get_events()) == 1
    future = datetime.now(UTC) + timedelta(days=1)
    count = bus.purge(before=future)
    assert count >= 1
    assert len(bus.get_events()) == 0

  def test_payload_json_valid(self, bus):
    """Le payload est bien du JSON."""
    payload = {"nested": {"key": "value"}, "list": [1, 2, 3], "null": None}
    bus.post_event("test.event", "chercheur", payload)
    events = bus.get_events()
    assert events[0]["payload"] == payload

  def test_status_stats(self, bus):
    """Le status retourne des statistiques cohérentes."""
    bus.post_event("health.updated", "defenseur", {"status": "ok"})
    bus.post_event("task.created", "intendant", {"action": "audit"}, targets=["defenseur"])
    st = bus.status()
    assert st["total"] == 2
    assert st["by_type"].get("health.updated", 0) >= 1
    assert st["by_type"].get("task.created", 0) >= 1
    assert st["by_source"].get("defenseur", 0) >= 1
    assert st["by_source"].get("intendant", 0) >= 1
    assert "pending" in st["by_status"]


class TestEventBusRules:
  """Vérifie les règles EVENT-1, EVENT-2, EVENT-3."""

  def test_event_3_integrity(self, bus):
    """EVENT-3 : la source est immuable après création."""
    eid1 = bus.post_event("health.updated", "defenseur", {"status": "ok"})
    eid2 = bus.post_event("task.created", "intendant", {"action": "backup"})
    events = bus.get_events()
    sources = {e["id"]: e["source"] for e in events}
    assert sources[eid1] == "defenseur"
    assert sources[eid2] == "intendant"

  def test_event_2_purge_ttl(self, bus):
    """EVENT-2 : le purge par défaut ne plante pas."""
    bus.post_event("old.event", "defenseur", {"data": "old"})
    count = bus.purge()
    assert count >= 0


class TestEventBusRuntime:
  """Tests runtime — cycles de vie réels des événements."""

  def test_full_event_lifecycle(self, bus):
    """pending → delivered → acknowledged."""
    eid = bus.post_event(
      "task.created", "intendant", {"action": "backup"}, targets=["defenseur"]
    )
    assert any(e["id"] == eid for e in bus.get_events(status="pending"))

    assert bus.mark_delivered(eid)
    assert any(e["id"] == eid for e in bus.get_events(status="delivered"))

    assert bus.ack_event(eid)
    assert any(e["id"] == eid for e in bus.get_events(status="acknowledged"))

  def test_broadcast_event(self, bus):
    """Sans targets, l'événement est visible par tous."""
    bus.post_event("alert.raised", "leviathan", {"level": "HAUT"})
    assert len(bus.get_events(target="intendant")) == 1
    assert len(bus.get_events(target="defenseur")) == 1

  def test_filter_by_source(self, bus):
    """Filtrage par source."""
    bus.post_event("health.updated", "defenseur", {"status": "ok"})
    bus.post_event("health.updated", "batisseur", {"status": "degraded"})
    assert len(bus.get_events(source="defenseur")) == 1
    assert len(bus.get_events(source="batisseur")) == 1

  def test_filter_by_type(self, bus):
    """Filtrage par type d'événement."""
    bus.post_event("health.updated", "defenseur", {"status": "ok"})
    bus.post_event("task.created", "intendant", {"action": "audit"})
    assert len(bus.get_events(event_type="health.updated")) == 1
    assert len(bus.get_events(event_type="task.created")) == 1

  def test_ordering_newest_first(self, bus):
    """Ordre DESC : le plus récent en premier."""
    bus.post_event("first.event", "defenseur", {"seq": 1})
    bus.post_event("second.event", "intendant", {"seq": 2})
    events = bus.get_events(limit=2)
    assert events[0]["payload"]["seq"] == 2
    assert events[1]["payload"]["seq"] == 1

  def test_limit_results(self, bus):
    """La limite du nombre de résultats est respectée."""
    for i in range(10):
      bus.post_event("test.event", "defenseur", {"i": i})
    assert len(bus.get_events(limit=3)) == 3

  def test_status_aggregation(self, bus):
    """Les statistiques reflètent l'état du bus."""
    for i in range(5):
      bus.post_event("test.event", "defenseur", {"i": i})
    st = bus.status()
    assert st["total"] == 5
    assert st["by_type"]["test.event"] == 5
    assert st["by_source"]["defenseur"] == 5
    assert st["by_status"].get("pending", 0) == 5
    assert st["oldest_event"] is not None
    assert st["newest_event"] is not None
    assert st["oldest_event"] <= st["newest_event"]

  def test_empty_bus(self, bus):
    """Un bus vide retourne des listes vides et un status à zéro."""
    assert bus.get_events() == []
    st = bus.status()
    assert st["total"] == 0
    assert st["by_type"] == {}
    assert st["by_source"] == {}
    assert st["by_status"] == {}
