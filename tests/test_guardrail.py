"""Tests du Kill Switch et des mécanismes de la Guardrail Layer."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


class TestKillSwitch:
  """Vérifie le mécanisme de Kill Switch dans shared-guardrail."""

  def test_kill_switch_protocol_in_skill(self, root):
    """shared-guardrail/SKILL.md doit mentionner le Kill Switch."""
    skill = (root / "skills" / "shared-guardrail" / "SKILL.md").read_text()
    assert "KILL" in skill, "shared-guardrail ne mentionne pas KILL"
    assert "stop" in skill, "shared-guardrail ne mentionne pas l'instruction stop"
    assert "freeze" in skill, "shared-guardrail ne mentionne pas l'instruction freeze"
    assert "rollback" in skill, "shared-guardrail ne mentionne pas l'instruction rollback"

  def test_kill_rules_complete(self, root):
    """Les règles KILL-1, KILL-2, KILL-3 sont implémentées dans le checker Python."""
    # KILL-1 Non-contournable — le Kill Switch est vérifié dans checker.py
    checker = (root / "polis" / "guardrail" / "checker.py").read_text()
    assert "KILL_PATH" in checker
    assert "_kill_switch_active" in checker

    # KILL-2 Pas d'auto-déclenchement — leviathan est le seul authorisé
    # (documenté dans shared-guardrail/SKILL.md)
    skill = (root / "skills" / "shared-guardrail" / "SKILL.md").read_text()
    assert "Kill Switch" in skill
    assert "stop" in skill
    assert "freeze" in skill
    assert "rollback" in skill
    assert "humain" in skill or "humaine" in skill


class TestPolisKillCommand:
  """Tests de la commande `polis kill`."""

  @pytest.fixture
  def mock_kill_dir(self):
    """Répertoire temporaire pour ~/.openclaw/."""
    tmp = Path(tempfile.mkdtemp())
    kill_file = tmp / "KILL"
    with patch("polis.polis.KILL_PATH", kill_file):
      yield tmp, kill_file
    shutil.rmtree(tmp, ignore_errors=True)

  def test_kill_status_no_file(self, mock_kill_dir):
    """`polis kill status` retourne 0 si KILL n'existe pas."""
    from polis.polis import cmd_kill_status

    assert cmd_kill_status() == 0

  def test_kill_set_and_clear(self, mock_kill_dir):
    """`polis kill set` puis `polis kill clear`."""
    tmp_dir, kill_file = mock_kill_dir
    from polis.polis import cmd_kill_clear, cmd_kill_set

    assert cmd_kill_set("stop") == 0
    assert kill_file.exists()
    assert kill_file.read_text().strip() == "stop"

    # clear (simuler confirmation)
    with patch("builtins.input", return_value="oui"):
      assert cmd_kill_clear() == 0
    assert not kill_file.exists()

  def test_kill_set_instruction_content(self, mock_kill_dir):
    """`polis kill set` écrit l'instruction exacte."""
    tmp_dir, kill_file = mock_kill_dir
    from polis.polis import cmd_kill_set

    cmd_kill_set("freeze")
    content = kill_file.read_text().strip()
    assert content == "freeze"

  def test_kill_status_with_file(self, mock_kill_dir):
    """`polis kill status` retourne 1 si KILL existe."""
    tmp_dir, kill_file = mock_kill_dir
    kill_file.write_text("stop\n")
    from polis.polis import cmd_kill_status

    assert cmd_kill_status() == 1
