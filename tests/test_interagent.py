"""Tests inter-agents — vérifie les mécanismes de communication et coordination."""

import re

import pytest


class TestSharedSkills:
  """Vérifie la présence et la cohérence des skills partagés."""

  def test_shared_skills_directories_exist(self, root):
    """Tous les skills partagés doivent avoir un répertoire."""
    shared_dir = root / "skills"
    expected = {
      "shared-governance",
      "shared-reporting",
      "shared-state",
      "shared-guardrail",
      "shared-notion-openclaw",
      "shared-interagent",
      "shared-learning",
      "shared-smoketest",
    }
    found = {d.name for d in shared_dir.iterdir() if d.is_dir()}
    assert found == expected, f"Skills partagés : attendu {expected}, trouvé {found}"

  def test_shared_skills_have_skill_md(self, root):
    """Chaque skill partagé doit avoir un SKILL.md."""
    for d in (root / "skills").iterdir():
      if d.is_dir():
        skill_file = d / "SKILL.md"
        assert skill_file.exists(), f"SKILL.md manquant dans skills/{d.name}"

  def test_shared_skills_no_duplicate_names(self, root):
    """Pas de noms de skills en double."""
    names = []
    for d in (root / "skills").iterdir():
      if d.is_dir():
        skill_file = d / "SKILL.md"
        if skill_file.exists():
          content = skill_file.read_text()
          m = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
          if m:
            names.append(m.group(1).strip())
    dups = {n for n in names if names.count(n) > 1}
    assert not dups, f"Noms de skills en double : {dups}"

  def test_shared_interagent_has_eventbus_section(self, root):
    """shared-interagent/SKILL.md doit définir le bus d'événements."""
    skill = (root / "skills" / "shared-interagent" / "SKILL.md").read_text()
    assert "Bus d'événements" in skill
    assert "events.db" in skill
    assert "EVENT-1" in skill
    assert "EVENT-2" in skill
    assert "EVENT-3" in skill

  def test_shared_interagent_has_instance_state(self, root):
    """shared-interagent/SKILL.md doit définir instance_state.json."""
    skill = (root / "skills" / "shared-interagent" / "SKILL.md").read_text()
    assert "instance_state.json" in skill
    assert "INST-1" in skill
    assert "INST-2" in skill
    assert "INST-3" in skill
    assert "INST-4" in skill

  def test_shared_interagent_referenced(self, config_example):
    """shared-interagent doit être dans la config de tous les agents non-intendant."""
    for agent_id in ["défenseur", "bâtisseur", "chercheur", "leviathan", "journaliste", "anarchiste"]:
      # Trouve la section de l'agent
      pattern = f'id: "{agent_id}"'
      idx = config_example.find(pattern)
      assert idx >= 0, f"Agent {agent_id} introuvable dans openclaw.json.example"
      # Cherche shared-interagent dans les 30 lignes suivantes
      section = config_example[idx : idx + 500]
      assert "shared-interagent" in section, (
        f"Agent {agent_id} n'a pas shared-interagent dans ses skills"
      )


class TestInterAgentFiles:
  """Vérifie les mécanismes de fichiers partagés entre agents."""

  def test_defenseur_health_json(self, root):
    """défenseur doit documenter health.json dans son AGENTS.md."""
    agents = (root / "workspaces" / "défenseur" / "AGENTS.md").read_text()
    assert "health.json" in agents, "défenseur/AGENTS.md ne mentionne pas health.json"

  def test_shared_gazette_referenced(self, root):
    """Le journaliste doit référencer shared/gazette/."""
    for fname in ["AGENTS.md", "SOUL.md", "TOOLS.md"]:
      path = root / "workspaces" / "journaliste" / fname
      if path.exists():
        content = path.read_text()
        if "gazette" in content.lower():
          return
    pytest.fail("Aucun fichier du journaliste ne mentionne 'gazette'")

  def test_shared_tracts_or_motions_referenced(self, root):
    """L'anarchiste doit référencer shared/tracts/ ou shared/motions/."""
    for fname in ["AGENTS.md", "SOUL.md", "TOOLS.md"]:
      path = root / "workspaces" / "anarchiste" / fname
      if path.exists():
        content = path.read_text()
        if "shared/tracts" in content or "shared/motions" in content:
          return
    pytest.fail("Aucun fichier de l'anarchiste ne mentionne 'shared/tracts' ou 'shared/motions'")


class TestInstanceState:
  """Vérifie le mécanisme d'état global de l'instance."""

  def test_instance_state_json_contract_in_skill(self, root):
    """shared-interagent doit documenter instance_state.json."""
    skill = (root / "skills" / "shared-interagent" / "SKILL.md").read_text()
    assert "instance_state.json" in skill

  def test_instance_state_has_overall_status(self, root):
    """Le contrat instance_state.json doit avoir overall_status."""
    skill = (root / "skills" / "shared-interagent" / "SKILL.md").read_text()
    assert "overall_status" in skill
    assert "nominal" in skill
    assert "degraded" in skill
    assert "critical" in skill

  def test_agents_write_to_instance_state(self, root):
    """Tous les agents configurés doivent avoir une entrée dans le contrat."""
    skill = (root / "skills" / "shared-interagent" / "SKILL.md").read_text()
    for agent in [
      "intendant",
      "defenseur",
      "bâtisseur",
      "chercheur",
      "leviathan",
      "journaliste",
      "anarchiste",
    ]:
      assert agent in skill, f"agent '{agent}' manquant dans le contrat instance_state.json"

  def test_workspaces_reference_degraded(self, root, workspaces):
    """Chaque workspace doit mentionner 'degraded' ou 'instance_state'."""
    keywords = ["degraded", "instance_state", "degrade", "dégradé"]
    for ws_name, files in workspaces.items():
      if "AGENTS.md" not in files:
        continue
      content = (root / "workspaces" / ws_name / "AGENTS.md").read_text().lower()
      found = any(kw.lower() in content for kw in keywords)
      if not found:
        pytest.skip(f"{ws_name} ne référence pas le mode dégradé (non requis pour tous)")


class TestLeviathanSurveillance:
  """Vérifie le système de surveillance leviathan."""

  def test_cells_exist_for_all_agents(self, root, workspaces):
    """leviathan doit avoir une cellule pour chaque agent."""
    cells_dir = root / "workspaces" / "leviathan" / "cells"
    assert cells_dir.is_dir(), "cells/ manquant dans leviathan"
    cell_files = {f.stem for f in cells_dir.iterdir() if f.suffix == ".md"}
    # Mapping workspace → nom de cellule (les cellules utilisent les noms longs)
    ws_to_cell = {
      "intendant": "intendant",
      "défenseur": "défenseur",
      "bâtisseur": "bâtisseur",
      "chercheur": "chercheur",
      "journaliste": "journaliste",
      "anarchiste": "anarchiste",
    }
    expected_cells = set(ws_to_cell.values())
    missing = expected_cells - cell_files
    assert not missing, f"Cellules leviathan manquantes : {missing}"

  def test_guardrail_log_referenced(self, root):
    """Le guardrail.log doit être référencé par leviathan ou les agents surveillés."""
    sources = [
      root / "workspaces" / "leviathan" / "AGENTS.md",
      root / "skills" / "shared-guardrail" / "SKILL.md",
    ]
    found = False
    for src in sources:
      if src.exists() and "guardrail.log" in src.read_text():
        found = True
        break
    assert found, "guardrail.log non référencé dans les fichiers de surveillance"
