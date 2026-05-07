"""Tests de configuration — valide openclaw.json.example et .env.example."""

import re

import pytest


class TestConfigStructure:
  """Structure et syntaxe de openclaw.json.example."""

  def test_braces_balanced(self, config_example):
    """Les accolades doivent être équilibrées."""
    opens = config_example.count("{")
    closes = config_example.count("}")
    assert opens == closes, f"Accolades déséquilibrées : {opens} ouvertes, {closes} fermées"

  def test_brackets_balanced(self, config_example):
    """Les crochets doivent être équilibrés."""
    opens = config_example.count("[")
    closes = config_example.count("]")
    assert opens == closes, f"Crochets déséquilibrés : {opens} ouverts, {closes} fermés"

  def test_seven_agents_configured(self, config_example):
    """openclaw.json.example doit configurer 7 agents."""
    count = config_example.count('id: "')
    assert count == 7, f"Attendu 7 agents, trouvé {count}"

  def test_gateway_present(self, config_example):
    """La section gateway doit être présente."""
    assert "gateway:" in config_example

  def test_channels_present(self, config_example):
    """La section channels doit être présente."""
    assert "channels:" in config_example
    assert "telegram:" in config_example

  def test_session_config_present(self, config_example):
    """La section session doit être présente."""
    assert "session:" in config_example


class TestEnvVars:
  """Cohérence entre openclaw.json.example et .env.example."""

  def test_config_refs_found_in_env(self, root, config_example):
    """Toutes les variables ${VAR} de openclaw.json doivent exister dans .env.example."""
    env_example = (root / ".env.example").read_text()
    refs = set(re.findall(r"\$\{([^}]+)\}", config_example))
    for ref in refs:
      assert ref in env_example, (
        f"Variable ${{{ref}}} dans openclaw.json.example introuvable dans .env.example"
      )

  @pytest.mark.parametrize(
    "required_var",
    [
      "TELEGRAM_BOT_TOKEN",
      "TELEGRAM_CHAT_ID",
      "NOTION_TOKEN",
      "NOTION_DB_PERSO_ID",
      "MAIL_ADDRESS",
      "MAIL_APP_PASSWORD",
      "OPENCLAW_GATEWAY_TOKEN",
    ],
  )
  def test_required_vars_present(self, root, required_var):
    """Les variables obligatoires doivent être dans .env.example."""
    env = (root / ".env.example").read_text()
    assert required_var in env, (
      f"Variable obligatoire {required_var} manquante dans .env.example"
    )

  def test_no_embedded_secrets(self, config_example):
    """Aucun secret réel ne doit être présent dans openclaw.json.example."""
    secrets_patterns = [
      r"sk-[a-zA-Z0-9]{20,}",
      r"secret_[a-f0-9]{32,}",
      r"ghp_[a-zA-Z0-9]{36,}",
    ]
    for pat in secrets_patterns:
      matches = re.findall(pat, config_example)
      assert not matches, f"Secret potentiel trouvé : {matches}"


class TestConfigCrossReference:
  """Vérifie la cohérence entre la config et DESCRIPTION.md."""

  def test_all_agents_in_description(self, config_example, description):
    """Tous les agents de openclaw.json doivent être documentés dans DESCRIPTION.md."""
    agents = re.findall(r'id:\s*"([^"]+)"', config_example)
    for agent in agents:
      assert agent in description, (
        f"Agent '{agent}' dans openclaw.json.example mais pas dans DESCRIPTION.md"
      )

  def test_agent_count_matches_across_files(self, config_example, readme, description):
    """Le nombre d'agents doit être le même dans config, README et DESCRIPTION."""
    config_count = config_example.count('id: "')
    # README: "7 agents"
    readme_match = re.search(r"(\d+)\s*agents", readme)
    assert readme_match, "README ne mentionne pas le nombre d'agents"
    assert int(readme_match.group(1)) == config_count, (
      f"README dit {readme_match.group(1)} agents, config en a {config_count}"
    )
