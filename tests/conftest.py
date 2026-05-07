"""Fixtures partagées pour les tests Polis."""

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def root() -> Path:
  """Racine du projet."""
  return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def constitution(root: Path) -> str:
  """Contenu de CONSTITUTION.md."""
  path = root / "CONSTITUTION.md"
  assert path.exists(), "CONSTITUTION.md introuvable"
  return path.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def config_example(root: Path) -> str:
  """Contenu de openclaw.json.example."""
  path = root / "openclaw.json.example"
  assert path.exists(), "openclaw.json.example introuvable"
  return path.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def description(root: Path) -> str:
  """Contenu de DESCRIPTION.md."""
  path = root / "DESCRIPTION.md"
  assert path.exists(), "DESCRIPTION.md introuvable"
  return path.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def readme(root: Path) -> str:
  """Contenu de README.md."""
  path = root / "README.md"
  assert path.exists(), "README.md introuvable"
  return path.read_text(encoding="utf-8")


WORKSPACE_FILES_REQUIRED = {
  "AGENTS.md",
  "SOUL.md",
  "IDENTITY.md",
  "TOOLS.md",
  "HEARTBEAT.md",
  "MEMORY.md",
}

WORKSPACES_WITH_USER = {"intendant", "chercheur"}


@pytest.fixture(scope="session")
def workspaces(root: Path):
  """Liste des répertoires workspace avec leurs fichiers."""
  ws_dir = root / "workspaces"
  assert ws_dir.is_dir(), "workspaces/ introuvable"
  result = {}
  for d in sorted(ws_dir.iterdir()):
    if d.is_dir():
      files = {f.name for f in d.iterdir() if f.is_file()}
      result[d.name] = files
  return result
