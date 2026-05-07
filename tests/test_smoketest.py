"""Tests du skill shared-smoketest et de la commande smoke de Polis."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


class TestSmoketestSkill:
  """Vérifie la présence et le contenu du skill shared-smoketest."""

  def test_smoketest_skill_exists(self, root):
    """Le répertoire shared-smoketest existe avec un SKILL.md."""
    skill_dir = root / "skills" / "shared-smoketest"
    assert skill_dir.is_dir(), "skills/shared-smoketest/ manquant"
    skill_file = skill_dir / "SKILL.md"
    assert skill_file.exists(), "SKILL.md manquant dans shared-smoketest"

  def test_smoketest_has_required_checks(self, root):
    """Le SKILL.md définit les vérifications obligatoires au démarrage."""
    skill = (root / "skills" / "shared-smoketest" / "SKILL.md").read_text()
    required = [
      "~/.openclaw/",
      "instance_state.json",
      "events.db",
      "AGENTS.md",
      "SMOKE_RESULT",
    ]
    for keyword in required:
      assert keyword in skill, f"shared-smoketest/SKILL.md ne mentionne pas '{keyword}'"

  def test_smoketest_has_smoke_result_format(self, root):
    """Le SKILL.md définit le format SMOKE_RESULT."""
    skill = (root / "skills" / "shared-smoketest" / "SKILL.md").read_text()
    assert "SMOKE_RESULT" in skill
    assert "continue | degraded | block" in skill

  def test_smoketest_has_rules(self, root):
    """Le SKILL.md définit des règles SMOKE-*."""
    skill = (root / "skills" / "shared-smoketest" / "SKILL.md").read_text()
    assert "SMOKE-1" in skill
    assert "SMOKE-2" in skill
    assert "SMOKE-3" in skill
    assert "SMOKE-4" in skill


class TestPolisSmokeCommand:
  """Tests de la commande `polis smoke run`."""

  def test_smoke_run_returns_zero_without_openclaw(self):
    """`polis smoke run` ne plante pas même sans ~/.openclaw/."""
    from polis.polis import cmd_smoke_run

    # Doit retourner 1 (échecs) sans ~/.openclaw/
    assert cmd_smoke_run() != 0

  @pytest.fixture
  def mock_openclaw(self):
    """Crée un ~/.openclaw/ temporaire avec les fichiers requis."""
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
          "agents": {},
        }
      )
    )
    with patch("pathlib.Path.home", return_value=tmp):
      yield tmp
    import shutil

    shutil.rmtree(tmp)

  def test_smoke_run_passes_with_openclaw(self, mock_openclaw):
    """`polis smoke run` passe si ~/.openclaw/ est présent."""
    from polis.polis import cmd_smoke_run

    assert cmd_smoke_run() == 0
