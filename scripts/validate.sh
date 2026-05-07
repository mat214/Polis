#!/usr/bin/env bash
# =============================================================================
# Script  : validate.sh
# Créé le  : 2026-05-06
# Auteur  : OpenClaw (CI)
# Raison  : Validation de cohérence du dépôt Polis
# Dépend de : bash >= 4, grep, awk, find, jq (optionnel), shellcheck (optionnel)
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ERRORS=0
WARNINGS=0

red()  { echo -e "\033[31m$1\033[0m"; }
green() { echo -e "\033[32m$1\033[0m"; }
yellow() { echo -e "\033[33m$1\033[0m"; }
fail()  { red " ✗ $1"; ERRORS=$((ERRORS+1)); }
pass()  { green " ✓ $1"; }
warn()  { yellow " ⚠ $1"; WARNINGS=$((WARNINGS+1)); }

echo "=== Validation OpenClaw — $(date) ==="
echo

# ── 0. ShellCheck (optionnel) ────────────────────────────────────────────────
echo "--- ShellCheck ---"
if command -v shellcheck &>/dev/null; then
  for script in "$0" "$ROOT/scripts/install.sh"; do
    name="$(basename "$script")"
    if shellcheck -S warning "$script" 2>/dev/null; then
      pass "$name : ShellCheck OK"
    else
      fail "$name : ShellCheck a détecté des problèmes"
    fi
  done
else
  warn "shellcheck non installé — vérification skipped"
fi
echo

# ── 1. Frontmatter SKILL.md ────────────────────────────────────────────────
echo "--- SKILL.md frontmatter ---"
# NOTE: Utilisation de process substitution (<(...)) au lieu d'un pipeline
# pour éviter le bug subshell qui masque les codes d'erreur.
# On ne lit que les 10 premières lignes pour rester dans le frontmatter YAML (---).
while read -r -d '' f; do
  dir="$(basename "$(dirname "$f")")"
  frontmatter="$(head -10 "$f")"

  # name field present and matches directory
  if ! echo "$frontmatter" | grep -q "^name: $dir$"; then
    fail "$f : name field missing or doesn't match directory ($dir)"
    continue
  fi
  pass "$dir : name OK"

  # description field present
  if ! echo "$frontmatter" | grep -q "^description:"; then
    fail "$f : description field missing"
    continue
  fi
  pass "$dir : description OK"

  # No forbidden fields
  if echo "$frontmatter" | grep -q "^version:" || echo "$frontmatter" | grep -q "^agents:"; then
    fail "$dir : contains forbidden field (version, agents)"
  fi
done < <(find "$ROOT/skills" "$ROOT/workspaces" -name SKILL.md -print0)

echo

# ── 2. Duplicate skill names ────────────────────────────────────────────────
echo "--- Duplicate skill names ---"
dups=$(find "$ROOT/skills" "$ROOT/workspaces" -name SKILL.md -exec grep -h "^name:" {} \; \
  | awk '{print $2}' | sort | uniq -d)
if [ -n "$dups" ]; then
  fail "Duplicate skill names: $(echo "$dups" | tr '\n' ' ')"
else
  pass "No duplicate skill names"
fi
echo

# ── 3. Skills referenced in openclaw.json exist ─────────────────────────────
echo "--- openclaw.json → skill directory mapping ---"
declare -A available_skills
while IFS= read -r -d '' f; do
  name=$(grep "^name:" "$f" 2>/dev/null | sed 's/^name: *//')
  [ -n "$name" ] && available_skills["$name"]=1
done < <(find "$ROOT/workspaces" "$ROOT/skills" -name SKILL.md -print0)

for skill in $(grep -oP '"\K(?:shared|int|def|bat|research|sec)-[^"]+' "$ROOT/openclaw.json.example" | sort -u || true); do
  if [ "${available_skills[$skill]:-}" = "1" ]; then
    pass "Skill '$skill' → found"
  else
    fail "Skill '$skill' referenced in openclaw.json but no SKILL.md found"
  fi
done
echo

# ── 4. Workspace files completeness ─────────────────────────────────────────
echo "--- Workspace files ---"
for ws in intendant défenseur bâtisseur chercheur leviathan journaliste anarchiste; do
  dir="$ROOT/workspaces/$ws"
  for f in AGENTS.md SOUL.md IDENTITY.md TOOLS.md HEARTBEAT.md; do
    if [ -f "$dir/$f" ]; then pass "$ws/$f"; else fail "$ws/$f missing"; fi
  done
  # USER.md for PA and chercheur
  if [ "$ws" = "intendant" ] || [ "$ws" = "chercheur" ]; then
    if [ -f "$dir/USER.md" ]; then
      pass "$ws/USER.md"
    fi
  fi
  # MEMORY.md for all
  if [ -f "$dir/MEMORY.md" ]; then
    pass "$ws/MEMORY.md"
  fi
done
echo

# ── 5. Cross-workspace governance consistency ────────────────────────────────
echo "--- Cross-workspace governance consistency ---"
for ws in défenseur bâtisseur chercheur leviathan journaliste; do
  f="$ROOT/workspaces/$ws/AGENTS.md"
  if grep -q "PA AGENTS.md\|shared governance\|N1/N2/N3" "$f" 2>/dev/null; then
    pass "$ws/AGENTS.md : references shared governance"
  else
    fail "$ws/AGENTS.md : missing governance reference"
  fi
done
echo

# ── 5b. Constitutional compliance ──────────────────────────────────────────
echo "--- Constitutional compliance ---"
if [ -f "$ROOT/CONSTITUTION.md" ]; then
  pass "CONSTITUTION.md : present"
  art_count=$(grep -c "^### Article" "$ROOT/CONSTITUTION.md" || true)
  if [ "$art_count" -ge 65 ]; then
    pass "CONSTITUTION.md : $art_count articles"
  else
    warn "CONSTITUTION.md : only $art_count articles (expected 65+)"
  fi
else
  fail "CONSTITUTION.md : missing"
fi

for ws in intendant défenseur bâtisseur chercheur leviathan journaliste anarchiste; do
  f="$ROOT/workspaces/$ws/AGENTS.md"
  if grep -qi "constitution\|CONSTITUTION" "$f" 2>/dev/null; then
    pass "$ws/AGENTS.md : references CONSTITUTION"
  else
    fail "$ws/AGENTS.md : no CONSTITUTION reference"
  fi
done

for ws in intendant défenseur bâtisseur chercheur leviathan journaliste anarchiste; do
  f="$ROOT/workspaces/$ws/SOUL.md"
  if grep -qi "constitution\|CONSTITUTION" "$f" 2>/dev/null; then
    pass "$ws/SOUL.md : references CONSTITUTION"
  else
    fail "$ws/SOUL.md : no CONSTITUTION reference"
  fi
done

# Check that openclaw.json has expected agents
expected_agents=7
all_agents=$(grep -c 'id: "' "$ROOT/openclaw.json.example" || true)
if [ "$all_agents" -ge "$expected_agents" ]; then
  pass "openclaw.json.example : $all_agents agents configured"
else
  fail "openclaw.json.example : only $all_agents agents (expected $expected_agents)"
fi
echo
# ── 5c. Cross-file agent count consistency ────────────────────────────
echo "--- Cross-file agent count consistency ---"
config_agents=$(grep -c 'id: "' "$ROOT/openclaw.json.example" || true)
install_agents=$(grep -oP "for ws in \K[^;]*" "$ROOT/scripts/install.sh" | wc -w)
desc_agents=$(grep -c "^├── workspace-\|^└── workspace-" "$ROOT/README.md" || true)
if [ "$config_agents" -eq "$install_agents" ] 2>/dev/null; then
  pass "install.sh : $install_agents agents (matches config)"
else
  fail "install.sh : $install_agents agents (config has $config_agents)"
fi
if [ "$config_agents" -eq "$desc_agents" ] 2>/dev/null; then
  pass "DESCRIPTION.md tree : $desc_agents agents (matches config)"
else
  warn "DESCRIPTION.md tree : $desc_agents agents (config has $config_agents)"
fi
echo

# ── 11. JSON5 syntax check (openclaw.json.example) ───────────────────────────
echo "--- JSON5 syntax ---"
config_file="$ROOT/openclaw.json.example"
if command -v jq &>/dev/null; then
  # jq ne gère pas les commentaires JSON5, donc on vire les lignes // et on teste
  cleaned=$(grep -v '^\s*//' "$config_file" 2>/dev/null || true)
  # Vérification basique : les accolades sont équilibrées
  opens=$(echo "$cleaned" | grep -o '{' | wc -l)
  closes=$(echo "$cleaned" | grep -o '}' | wc -l)
  if [ "$opens" -eq "$closes" ]; then
    pass "openclaw.json.example : braces balanced ($opens)"
  else
    fail "openclaw.json.example : unbalanced braces (open=$opens close=$closes)"
  fi
  # Vérification des crochets
  opens=$(echo "$cleaned" | grep -o '\[' | wc -l)
  closes=$(echo "$cleaned" | grep -o '\]' | wc -l)
  if [ "$opens" -eq "$closes" ]; then
    pass "openclaw.json.example : brackets balanced ($opens)"
  else
    fail "openclaw.json.example : unbalanced brackets"
  fi
  # Variable interpolation sanity check
  bad_refs=$(grep -oP '\$\{[^}]+\}' "$config_file" | sort -u | \
    while read -r var; do
      varname=${var#\$\{}
      varname=${varname%\}}
      # Variables définies dans .env.example
      grep -q "$varname" "$ROOT/.env.example" 2>/dev/null || echo "$varname"
    done)
  if [ -n "$bad_refs" ]; then
    warn "Variables in openclaw.json.example not in .env.example: $(echo "$bad_refs" | tr '\n' ' ')"
  else
    pass "openclaw.json.example : all variable refs found in .env.example"
  fi
else
  warn "jq not installed — JSON5 brace balance and variable check skipped"
fi
echo

# ── 11. .env.example sanity checks ───────────────────────────────────────────
echo "--- .env.example ---"
env_file="$ROOT/.env.example"
empty_vars=$(grep -c '=' "$env_file" 2>/dev/null || true)
if [ "$empty_vars" -gt 10 ]; then
  pass ".env.example : $empty_vars variables documented"
else
  fail ".env.example : suspiciously few variables ($empty_vars)"
fi

# Check for any real secrets accidentally committed
if grep -qiP '(sk-[a-zA-Z0-9]{20,}|secret_[a-f0-9]{32,}|ghp_[a-zA-Z0-9]{36,})' "$ROOT/openclaw.json.example" 2>/dev/null; then
  fail "Possible secret values found in openclaw.json.example!"
else
  pass "openclaw.json.example : no embedded secrets"
fi
echo

# ── 11. DESCRIPTION.md ↔ openclaw.json.example cross-ref ─────────────────────
echo "--- Cross-documentation consistency ---"
desc_file="$ROOT/DESCRIPTION.md"
# Vérifier que les agents listés dans openclaw.json.example sont documentés
config_agents=$(grep -oP 'id:\s*"\K[^"]+' "$ROOT/openclaw.json.example" | sort -u || true)
for agent in $config_agents; do
  if grep -qi "Agent \`$agent" "$desc_file" 2>/dev/null || grep -qi "$agent" "$desc_file" 2>/dev/null; then
    pass "Agent '$agent' documented in DESCRIPTION.md"
  else
    warn "Agent '$agent' in config but not documented in DESCRIPTION.md"
  fi
done
echo

# ── 11. CHANGELOG.md has recent entries ──────────────────────────────────────
echo "--- CHANGELOG.md freshness ---"
if [ -f "$ROOT/CHANGELOG.md" ]; then
  last_date=$(grep -oP '\[\K\d{4}-\d{2}-\d{2}' "$ROOT/CHANGELOG.md" | head -1 || true)
  if [ -n "$last_date" ]; then
    pass "CHANGELOG.md : last entry $last_date"
  fi
else
  warn "CHANGELOG.md missing"
fi
echo

# ── 11. Gitignore sanity ────────────────────────────────────────────────────
echo "--- .gitignore coverage ---"
if [ -f "$ROOT/.gitignore" ]; then
  for pattern in ".env" "node_modules/" "*.log" "__pycache__"; do
    if grep -q "$pattern" "$ROOT/.gitignore"; then
      pass ".gitignore : '$pattern' present"
    else
      warn ".gitignore : '$pattern' missing"
    fi
  done
fi
echo

# ── Result ──────────────────────────────────────────────────────────────────
echo "=== Result: $ERRORS error(s), $WARNINGS warning(s) ==="
if [ "$ERRORS" -gt 0 ]; then
  red "Certaines vérifications ont échoué. Consultez les détails ci-dessus."
fi
exit "$ERRORS"
