"""Tests runtime des commandes Polis CLI.

Ces tests créent de vrais fichiers temporaires et exercent les commandes
pour vérifier leur comportement — pas seulement du parsing de markdown.
"""

import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def mock_openclaw():
  """Crée une arborescence ~/.openclaw/ temporaire complète."""
  tmp = Path(tempfile.mkdtemp())
  openclaw_dir = tmp / ".openclaw"
  shared = openclaw_dir / "shared"
  shared.mkdir(parents=True)

  state_file = shared / "instance_state.json"
  state_file.write_text(
    json.dumps(
      {
        "updated_at": "2026-01-01T00:00:00Z",
        "overall_status": "nominal",
        "agents": {
          "defenseur": {
            "status": "ok",
            "capabilities": ["audit"],
            "since": "2026-01-01T00:00:00Z",
          },
          "intendant": {
            "status": "ok",
            "capabilities": ["mail"],
            "since": "2026-01-01T00:00:00Z",
          },
        },
      }
    )
  )
  with patch("pathlib.Path.home", return_value=tmp):
    yield tmp
  shutil.rmtree(tmp)


class TestKillCommandRuntime:
  """Tests runtime de la commande kill."""

  @pytest.fixture
  def mock_kill(self):
    tmp = Path(tempfile.mkdtemp())
    kill_file = tmp / "KILL"
    with patch("polis.polis.KILL_PATH", kill_file):
      yield tmp, kill_file
    shutil.rmtree(tmp, ignore_errors=True)

  def test_kill_status_no_file(self, mock_kill):
    from polis.polis import cmd_kill_status

    assert cmd_kill_status() == 0

  def test_kill_set_stop(self, mock_kill):
    from polis.polis import cmd_kill_set

    assert cmd_kill_set("stop") == 0
    _, kill_file = mock_kill
    assert kill_file.read_text().strip() == "stop"

  def test_kill_set_freeze(self, mock_kill):
    from polis.polis import cmd_kill_set

    assert cmd_kill_set("freeze") == 0
    _, kill_file = mock_kill
    assert kill_file.read_text().strip() == "freeze"

  def test_kill_status_active(self, mock_kill):
    _, kill_file = mock_kill
    kill_file.write_text("stop\n")
    from polis.polis import cmd_kill_status

    assert cmd_kill_status() == 1 # actif → code 1

  def test_kill_clear(self, mock_kill):
    _, kill_file = mock_kill
    kill_file.write_text("stop\n")
    from polis.polis import cmd_kill_clear

    with patch("builtins.input", return_value="oui"):
      assert cmd_kill_clear() == 0
    assert not kill_file.exists()

  def test_kill_clear_denies_noninteractive(self, mock_kill):
    """En mode non-interactif (EOFError), le kill n'est pas supprimé."""
    _, kill_file = mock_kill
    kill_file.write_text("stop\n")
    from polis.polis import cmd_kill_clear

    with patch("builtins.input", side_effect=EOFError):
      assert cmd_kill_clear() == 1 # refusé
    assert kill_file.exists()


class TestStateCommandRuntime:
  """Tests runtime de la commande state status."""

  def test_state_status_no_file(self):
    """Sans instance_state.json, retourne code 1."""
    from polis.polis import cmd_state_status

    with patch("pathlib.Path.home", return_value=Path(tempfile.mkdtemp())):
      assert cmd_state_status() == 1

  def test_state_status_with_file(self, mock_openclaw):
    """Avec instance_state.json, affiche l'état global."""
    from polis.polis import cmd_state_status

    assert cmd_state_status() == 0


class TestCheckCommandsRuntime:
  """Tests runtime des commandes check."""

  def test_check_degraded_passes_with_smoketest(self, root):
    """check degraded passe car shared-smoketest existe."""
    from polis.polis import cmd_check_degraded

    assert cmd_check_degraded() == 0

  def test_check_constitution_passes(self, root):
    """check constitution passe avec 71 articles."""
    from polis.polis import cmd_check_constitution

    assert cmd_check_constitution() == 0

  def test_check_agents_passes(self, root):
    """check agents passe avec tous les workspaces."""
    from polis.polis import cmd_check_agents

    assert cmd_check_agents() == 0

  def test_check_config_passes(self, root):
    """check config passe avec 7 agents."""
    from polis.polis import cmd_check_config

    assert cmd_check_config() == 0
