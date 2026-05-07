#!/usr/bin/env bash
# =============================================================================
# Script  : install.sh
# Créé le  : 2026-05-06
# Auteur  : OpenClaw
# Raison  : Déploiement automatisé de l'instance OpenClaw
# Usage   : bash install.sh [--workspace DIR] [--dry-run]
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
DRY_RUN=false

# Couleurs
red()  { echo -e "\033[31m$1\033[0m"; }
green() { echo -e "\033[32m$1\033[0m"; }
yellow() { echo -e "\033[33m$1\033[0m"; }

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Déploie la configuration OpenClaw de référence vers \$OPENCLAW_HOME.

Options:
 --workspace DIR  Répertoire de destination (défaut: ~/.openclaw)
 --dry-run     Simule les actions sans rien copier
 --help      Affiche cette aide
EOF
  exit 0
}

while [ $# -gt 0 ]; do
  case "$1" in
    --workspace) OPENCLAW_HOME="$2"; shift 2 ;;
    --dry-run)  DRY_RUN=true; shift ;;
    --help)   usage ;;
    *)      red "Option inconnue: $1"; usage ;;
  esac
done

echo "=== OpenClaw Installer ==="
echo "Source : $ROOT"
echo "Cible : $OPENCLAW_HOME"
$DRY_RUN && yellow "Mode DRY-RUN — aucune copie réelle"
echo

# Vérifications préalables
pre_flight() {
  echo "--- Pré-vérifications ---"
  local ok=true

  if [ -d "$OPENCLAW_HOME" ]; then
    yellow " ⚠ $OPENCLAW_HOME existe déjà"
    yellow "  Les fichiers existants ne seront pas écrasés (cp -n)"
  fi

  for dir in skills workspaces; do
    if [ -d "$ROOT/$dir" ]; then
      green " ✓ $dir/ présent"
    else
      red " ✗ $dir/ manquant dans $ROOT"
      ok=false
    fi
  done

  for f in openclaw.json.example .env.example; do
    if [ -f "$ROOT/$f" ]; then
      green " ✓ $f présent"
    else
      red " ✗ $f manquant dans $ROOT"
      ok=false
    fi
  done

  $ok || { red "Pré-vérifications échouées. Abandon."; exit 1; }
  echo
}

deploy() {
  echo "--- Déploiement ---"

  # Créer la structure
  if $DRY_RUN; then
    yellow " ~ mkdir -p $OPENCLAW_HOME $OPENCLAW_HOME/shared $OPENCLAW_HOME/shared/gazette $OPENCLAW_HOME/shared/revendications"
  else
    mkdir -p "$OPENCLAW_HOME" "$OPENCLAW_HOME/shared" "$OPENCLAW_HOME/shared/gazette" "$OPENCLAW_HOME/shared/revendications"
  fi

  # Skills partagés
  echo " Skills partagés → $OPENCLAW_HOME/skills/"
  if $DRY_RUN; then
    yellow "  cp -rn $ROOT/skills/* $OPENCLAW_HOME/skills/"
  else
    mkdir -p "$OPENCLAW_HOME/skills"
    cp -rn "$ROOT/skills"/* "$OPENCLAW_HOME/skills/" 2>/dev/null || true
    green " ✓ Skills partagés copiés"
  fi

  # Workspaces
  for ws in intendant défenseur bâtisseur chercheur leviathan journaliste anarchiste; do
    echo " Workspace $ws → $OPENCLAW_HOME/workspace-$ws/"
    if $DRY_RUN; then
      yellow "  cp -rn $ROOT/workspaces/$ws/. $OPENCLAW_HOME/workspace-$ws/"
    else
      mkdir -p "$OPENCLAW_HOME"
      cp -rn "$ROOT/workspaces/$ws/." "$OPENCLAW_HOME/workspace-$ws/" 2>/dev/null || true
      green " ✓ Workspace $ws copié"
    fi
  done

  # Recherche
  echo " Recherche → $OPENCLAW_HOME/research/"
  if $DRY_RUN; then
    yellow "  mkdir -p $OPENCLAW_HOME/research/projects $OPENCLAW_HOME/research/monthly_reports"
  else
    mkdir -p "$OPENCLAW_HOME/research/projects" "$OPENCLAW_HOME/research/monthly_reports"
    # Copier les projets de recherche
    if [ -d "$ROOT/workspaces/chercheur/projects" ]; then
      cp -rn "$ROOT/workspaces/chercheur/projects/." "$OPENCLAW_HOME/research/projects/" 2>/dev/null || true
    fi
    green " ✓ Recherche initialisée"
  fi

  # Configuration (ne pas écraser existant)
  if [ -f "$OPENCLAW_HOME/openclaw.json" ]; then
    yellow " openclaw.json existe déjà — création de openclaw.json.new"
    $DRY_RUN || cp -n "$ROOT/openclaw.json.example" "$OPENCLAW_HOME/openclaw.json.new"
  else
    $DRY_RUN || cp -n "$ROOT/openclaw.json.example" "$OPENCLAW_HOME/openclaw.json"
    green " ✓ openclaw.json copié"
  fi

  # .env (ne pas écraser existant)
  if [ -f "$OPENCLAW_HOME/.env" ]; then
    yellow " .env existe déjà — inchangé"
  else
    if $DRY_RUN; then
      yellow "  cp -n $ROOT/.env.example $OPENCLAW_HOME/.env"
    else
      cp -n "$ROOT/.env.example" "$OPENCLAW_HOME/.env"
      green " ✓ .env copié (à éditer avec vos tokens)"
    fi
  fi

  echo
}

post_install() {
  echo "--- Post-installation ---"
  echo
  green " Déploiement terminé !"
  echo
  echo " Prochaines étapes :"
  echo " 1. Éditer $OPENCLAW_HOME/.env avec vos tokens"
  echo " 2. Adapter $OPENCLAW_HOME/openclaw.json si nécessaire"
  echo " 3. Lancer : openclaw setup --workspace $OPENCLAW_HOME/workspace-intendant"
  echo
  echo " Pour valider : bash $ROOT/scripts/validate.sh"
  echo " Pour installer les cron : cf. DESCRIPTION.md section Tâches planifiées"
}

pre_flight
deploy
$DRY_RUN || post_install
