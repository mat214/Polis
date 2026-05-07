"""Tests constitutionnels — vérifie que CONSTITUTION.md est cohérente et applicable."""

import re


class TestConstitutionStructure:
  """Structure et cohérence interne de la constitution."""

  def test_articles_present(self, constitution):
    """La constitution doit contenir des articles."""
    articles = re.findall(r"^### Article \d+", constitution, re.MULTILINE)
    assert len(articles) >= 70, f"Attendu ≥70 articles, trouvé {len(articles)}"

  def test_article_numbering_continuous(self, constitution):
    """La numérotation des articles doit être continue de 1 à N (bis/ter exclus)."""
    expected = 1
    for line in constitution.splitlines():
      m = re.match(r"### Article (\d+)(bis|ter|quater)?", line)
      if m:
        base = int(m.group(1))
        suffix = m.group(2) or ""
        if not suffix:
          assert base == expected, (
            f"Article {expected} attendu, trouvé Article {base}"
          )
          expected += 1
        # Les articles suffixés (bis/ter) sont ignorés dans le comptage linéaire

  def test_titles_present(self, constitution):
    """Tous les titres (I à XII) doivent être présents."""
    roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
    for num in roman:
      assert f"TITRE {num}" in constitution, f"TITRE {num} manquant"

  def test_preambule_present(self, constitution):
    """Le préambule doit mentionner les quatre forces."""
    assert "quatre forces" in constitution
    assert "innovation" in constitution.lower()
    assert "stabilité" in constitution or "stabilite" in constitution

  def test_article_1_primacy(self, constitution):
    """Article 1 : primauté de l'utilisateur."""
    assert "Article 1" in constitution
    assert "Primauté de l'utilisateur" in constitution

  def test_article_29_human_gate(self, constitution):
    """Article 29 : Human-in-the-Loop pour les actions irréversibles."""
    assert "Article 29" in constitution
    assert "irréversible" in constitution.lower() or "irreversible" in constitution.lower()
    assert "confirmation humaine" in constitution

  def test_article_45_conflict_reporting(self, constitution):
    """Article 45 : signalement des conflits."""
    assert "Article 45" in constitution
    assert "incohérence" in constitution or "incoherence" in constitution

  def test_article_71_civic_tech(self, constitution):
    """Article 71 : devoir de civic-tech."""
    assert "Article 71" in constitution
    assert "civic-tech" in constitution or "civic tech" in constitution


class TestConstitutionSubordination:
  """Hiérarchie normative — la constitution prévaut."""

  def test_prevails_over_instructions(self, constitution):
    """La constitution doit prévaloir sur les instructions reçues."""
    assert "prévaut" in constitution or "prevaut" in constitution

  def test_leviathan_cannot_block_without_citation(self, constitution):
    """Article 56 : leviathan ne peut pas bloquer sans citer d'article."""
    assert "Article 56" in constitution
    lines = constitution.splitlines()
    in_art56 = False
    article_text = []
    for line in lines:
      if line.startswith("### Article 56"):
        in_art56 = True
      elif in_art56 and line.startswith("### Article"):
        break
      if in_art56:
        article_text.append(line)
    section = "\n".join(article_text)
    assert "ne peut pas" in section or "ne peut" in section, (
      "Article 56 ne contient pas de limite explicite"
    )


class TestConstitutionApplicability:
  """La constitution doit être applicable par un agent LLM."""

  def test_actionable_rules(self, constitution):
    """Les articles doivent contenir des règles actionnables (verbes d'action)."""
    action_verbs = ["doit", "peut", "ne peut", "est", "sont", "a le droit"]
    article_lines = [
      line
      for line in constitution.splitlines()
      if line.startswith("###") or line.strip().startswith("-")
    ]
    actionable = sum(
      1 for line in article_lines if any(v in line.lower() for v in action_verbs)
    )
    ratio = actionable / max(len(article_lines), 1)
    # Au moins 10% des lignes doivent être actionnables (les articles
    # contiennent aussi du contexte, des titres et des descriptions)
    assert ratio > 0.10, f"Seulement {ratio:.0%} des lignes sont actionnables"

  def test_defined_levels(self, constitution):
    """Les niveaux N1, N2, N3 doivent être définis."""
    assert "N1" in constitution
    assert "N2" in constitution
    assert "N3" in constitution

  def test_suspicion_levels_defined(self, constitution):
    """Les niveaux de suspicion leviathan doivent être définis."""
    for level in ["safe", "suspect", "dangerous", "subversive"]:
      assert level in constitution, f"Niveau de suspicion '{level}' manquant"

  def test_force_names_defined(self, constitution):
    """Les quatre forces constitutionnelles doivent être nommées."""
    forces = ["Innovation", "Infrastructure", "Stabilité", "Transparence"]
    for force in forces:
      assert force.lower() in constitution.lower(), f"Force '{force}' manquante"


class TestConstitutionCrossReference:
  """Vérification des références croisées avec les workspaces."""

  def test_agent_files_reference_constitution(self, root, workspaces):
    """Tous les AGENTS.md doivent référencer la constitution."""
    for ws_name in workspaces:
      agents_path = root / "workspaces" / ws_name / "AGENTS.md"
      if agents_path.exists():
        content = agents_path.read_text()
        assert "constitution" in content.lower() or "CONSTITUTION" in content, (
          f"{ws_name}/AGENTS.md ne référence pas la constitution"
        )

  def test_soul_files_reference_constitution(self, root, workspaces):
    """Tous les SOUL.md doivent référencer la constitution."""
    for ws_name in workspaces:
      soul_path = root / "workspaces" / ws_name / "SOUL.md"
      if soul_path.exists():
        content = soul_path.read_text()
        assert "constitution" in content.lower() or "CONSTITUTION" in content, (
          f"{ws_name}/SOUL.md ne référence pas la constitution"
        )
