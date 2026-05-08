"""Package Polis — configuration dans pyproject.toml (source de vérité)."""
from setuptools import find_packages, setup

setup(
  name="polis",
  version="0.2.0",
  description="Architecture de référence OpenClaw — CLI de validation et bus d'événements",
  packages=find_packages(),
  python_requires=">=3.12",
  install_requires=[],
  extras_require={
    "dev": [
      "pytest>=7",
      "coverage>=7",
      "ruff>=0.4",
      "mypy>=1.8",
    ],
  },
  entry_points={
    "console_scripts": [
      "polis=polis:main",
    ],
  },
)
