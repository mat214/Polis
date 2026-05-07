"""Tests des workspaces — vérifie la complétude et la cohérence des agents."""

import pytest


class TestWorkspaceCompleteness:
  """Chaque workspace doit avoir les fichiers requis."""

  def test_all_workspaces_have_required_files(self, workspaces):
    """Vérifie que tous les workspaces ont AGENTS, SOUL, IDENTITY, TOOLS, HEARTBEAT, MEMORY."""
    from conftest import WORKSPACE_FILES_REQUIRED

    for ws_name, files in workspaces.items():
      missing = WORKSPACE_FILES_REQUIRED - files
      assert not missing, f"{ws_name} : fichiers manquants : {missing}"

  def test_pa_and_chercheur_have_user(self, workspaces):
    """PA et chercheur doivent avoir USER.md."""
    from conftest import WORKSPACES_WITH_USER

    for ws_name in WORKSPACES_WITH_USER:
      assert ws_name in workspaces, f"Workspace {ws_name} manquant"
      assert "USER.md" in workspaces[ws_name], f"{ws_name} : USER.md manquant"

  def test_other_workspaces_no_user(self, workspaces):
    """Les autres workspaces ne doivent PAS avoir USER.md."""
    from conftest import WORKSPACES_WITH_USER

    for ws_name, files in workspaces.items():
      if ws_name not in WORKSPACES_WITH_USER:
        assert "USER.md" not in files, f"{ws_name} ne devrait pas avoir USER.md"

  def test_seven_workspaces(self, workspaces):
    """Il doit y avoir exactement 7 workspaces."""
    assert len(workspaces) == 7, (
      f"Attendu 7 workspaces, trouvé {len(workspaces)} : {list(workspaces.keys())}"
    )

  def test_workspace_names(self, workspaces):
    """Les noms de workspaces doivent être ceux attendus."""
    expected = {
      "intendant",
      "défenseur",
      "bâtisseur",
      "chercheur",
      "leviathan",
      "journaliste",
      "anarchiste",
    }
    assert set(workspaces.keys()) == expected, (
      f"Workspaces attendus : {expected}, trouvés : {set(workspaces.keys())}"
    )


class TestWorkspaceSkills:
  """Vérifie la cohérence des skills entre les workspaces et la config."""

  def test_skills_directories_exist(self, root, workspaces):
    """Chaque workspace doit avoir un répertoire skills/."""
    for ws_name in workspaces:
      skills_dir = root / "workspaces" / ws_name / "skills"
      assert skills_dir.is_dir(), f"{ws_name} : skills/ manquant"

  @pytest.mark.parametrize(
    "ws_name,expected_skills",
    [
      (
        "intendant",
        {
          "int-calendar",
          "int-contacts",
          "int-daily-brief",
          "int-mail",
          "int-memory",
          "int-notion",
          "int-tasks",
          "int-telegram",
        },
      ),
      (
        "défenseur",
        {
          "def-audit",
          "def-backup",
          "def-bootstrap",
          "def-defense",
          "def-maintenance",
          "def-remediation",
          "def-update",
        },
      ),
      (
        "bâtisseur",
        {
          "bat-audit",
          "bat-bootstrap",
          "bat-capabilities",
          "bat-packages",
          "bat-rollback",
          "bat-scripts",
          "bat-services",
        },
      ),
      ("chercheur", {"research-core", "research-learn"}),
      ("leviathan", {"sec-doctrine", "sec-enforcement", "sec-surveillance"}),
      ("journaliste", {"journal-gazette", "journal-reporting"}),
      ("anarchiste", {"anarchiste-tract", "anarchiste-motion", "anarchiste-probe", "anarchiste-bilan"}),
    ],
  )
  def test_skills_match_expected(self, root, ws_name, expected_skills):
    """Les skills présents dans chaque workspace doivent correspondre aux attendus."""
    skills_dir = root / "workspaces" / ws_name / "skills"
    found = {d.name for d in skills_dir.iterdir() if d.is_dir()}
    assert found == expected_skills, (
      f"{ws_name} : skills attendus {expected_skills}, trouvés {found}"
    )


class TestWorkspaceGovernance:
  """Vérifie la cohérence de la gouvernance entre workspaces."""

  def test_journaliste_references_governance(self, root):
    """Le journaliste doit référencer la gouvernance partagée."""
    agents = (root / "workspaces" / "journaliste" / "AGENTS.md").read_text()
    assert "N1" in agents and "N2" in agents and "N3" in agents, (
      "journaliste/AGENTS.md doit référencer N1/N2/N3"
    )

  @pytest.mark.parametrize(
    "ws_name", ["défenseur", "bâtisseur", "chercheur", "leviathan", "journaliste"]
  )
  def test_cross_workspace_governance_consistency(self, root, ws_name):
    """Les AGENTS.md de ces workspaces doivent référencer la gouvernance."""
    path = root / "workspaces" / ws_name / "AGENTS.md"
    content = path.read_text()
    has_governance = any(
      keyword in content
      for keyword in ["N1/N2/N3", "shared governance", "gouvernance partagée", "Gouvernance"]
    )
    assert has_governance, f"{ws_name}/AGENTS.md ne référence pas la gouvernance partagée"
