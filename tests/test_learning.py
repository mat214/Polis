"""Tests du système d'apprentissage et de la validation croisée mémoire."""


class TestLearningCrossValidation:
  """Vérifie la validation croisée mémoire dans shared-learning."""

  def test_learning_has_cross_validation_cycle(self, root):
    """shared-learning/SKILL.md doit mentionner la validation croisée dans son cycle."""
    skill = (root / "skills" / "shared-learning" / "SKILL.md").read_text()
    assert "validation croisée" in skill.lower(), (
      "shared-learning ne mentionne pas la validation croisée dans le cycle"
    )

  def test_learning_has_learn_numbering(self, root):
    """shared-learning/SKILL.md doit avoir une numérotation LEARN (1-5)."""
    skill = (root / "skills" / "shared-learning" / "SKILL.md").read_text()
    for label in ["LEARN-1", "LEARN-2", "LEARN-3/4", "LEARN-5"]:
      assert label in skill, f"shared-learning ne définit pas {label}"

  def test_learning_mentions_contestation_window(self, root):
    """shared-learning doit mentionner la fenêtre de contestation 48h."""
    skill = (root / "skills" / "shared-learning" / "SKILL.md").read_text()
    assert "contestation" in skill.lower() or "48h" in skill, (
      "shared-learning ne mentionne pas la fenêtre de contestation"
    )

  def test_learning_mentions_shared_proposals(self, root):
    """shared-learning doit mentionner shared/learning_proposals/."""
    skill = (root / "skills" / "shared-learning" / "SKILL.md").read_text()
    assert "learning_proposals" in skill, (
      "shared-learning ne mentionne pas learning_proposals"
    )


class TestLeviathanCrossValidation:
  """Vérifie que leviathan a connaissance du cycle d'apprentissage actuel."""

  def test_leviathan_references_learning_cycle(self, root):
    """leviathan/AGENTS.md doit mentionner la validation croisée mémoire et son évolution."""
    agents = (root / "workspaces" / "leviathan" / "AGENTS.md").read_text()
    assert "validation croisée" in agents.lower() or "apprentissage" in agents.lower(), (
      "leviathan/AGENTS.md ne mentionne pas la validation croisée ou l'apprentissage"
    )

  def test_leviathan_has_five_pillars(self, root):
    """leviathan/AGENTS.md doit avoir exactement 5 piliers (le 6e a été supprimé)."""
    agents = (root / "workspaces" / "leviathan" / "AGENTS.md").read_text()
    assert "cinq piliers" in agents or "5 piliers" in agents or (
      "cinq" in agents and "piliers" in agents
    ), "leviathan/AGENTS.md n'annonce pas 5 piliers"
    # Vérifie la mention du 6e pilier supprimé
    assert "sixième pilier" in agents.lower(), (
      "leviathan/AGENTS.md doit documenter la disparition du 6e pilier"
    )

  def test_interagent_contract_has_learning_proposals(self, root):
    """Le contrat shared-interagent doit inclure learning_proposals."""
    skill = (root / "skills" / "shared-interagent" / "SKILL.md").read_text()
    assert "learning_proposals" in skill, (
      "shared-interagent ne définit pas learning_proposals"
    )
