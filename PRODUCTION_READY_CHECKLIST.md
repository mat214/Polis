# Production-Ready Checklist — Polis (OpenClaw)

> Validation de la conformité du dépôt pour un déploiement en conditions réelles.
> Chaque critère doit être vérifié (✅) avant de considérer l'instance comme "production-ready".

---

## 1. Structure et architecture (CTO)

| Critère | Statut | Remarque |
|---|---|---|
| Arborescence cohérente (workspaces, skills, config) | ✅ | skills/, workspaces/, scripts/ |
| Pas de code mort ou fichiers orphelins | ✅ | Nettoyé au Chantier 4 |
| Pas de duplication de responsabilités entre skills | ✅ | skills spécialisés par agent |
| Configuration JSON5 syntaxiquement correcte | ✅ | Vérifié par validate.sh |
| Fichier `.env.example` complet et à jour | ✅ | 34 variables documentées |
| Tous les agents ont leurs fichiers standard | ✅ | AGENTS, SOUL, IDENTITY, TOOLS, HEARTBEAT, MEMORY |
| Makefile ou task runner pour les opérations courantes | ✅ | `make validate`, `make install`, `make lint` |
| CONSTITUTION.md existe et est référencée | ✅ | 71 articles, 12 titres, référencée dans tous les AGENTS.md |

## 2. Tests et validation (QA)

| Critère | Statut | Remarque |
|---|---|---|
| Script de validation automatisé | ✅ | `scripts/validate.sh` — 10 catégories de tests |
| Validation des frontmatter SKILL.md (name + description) | ✅ | Vérifié par validate.sh |
| Pas de noms de skills en double | ✅ | Vérifié par validate.sh |
| Cohérence config→skills | ✅ | Vérifié par validate.sh |
| Cohérence inter-workspaces (gouvernance N1/N2/N3) | ✅ | Vérifié par validate.sh |
| Syntaxe JSON5 (accolades/crochets équilibrés) | ✅ | Vérifié par validate.sh |
| Cross-refs documentation (config → DESCRIPTION.md) | ✅ | Vérifié par validate.sh |
| Couverture `.gitignore` (secrets, logs, caches) | ✅ | Vérifié par validate.sh |
| Tous les tests passent en < 30s | ✅ | Le validate.sh s'exécute en < 5s |

## 3. CI/CD et déploiement (DevOps)

| Critère | Statut | Remarque |
|---|---|---|
| GitHub Actions sur push + PR | ✅ | `.github/workflows/validate.yml` |
| ShellCheck sur tous les scripts bash | ✅ | Exécuté dans le workflow CI |
| Job Makefile séparé dans la CI | ✅ | Vérifie `make validate` + `make lint` |
| Script de déploiement automatisé | ✅ | `scripts/install.sh` (supporte --dry-run) |
| Installation en 3 commandes max | ✅ | Voir README.md section Installation |
| Makefile pour les opérations courantes | ✅ | `validate`, `install`, `lint` |

## 4. Sécurité (Security Officer)

| Critère | Statut | Remarque |
|---|---|---|
| Fichier `.gitleaks.toml` pour réduire faux positifs | ✅ | Allowlist des patterns doc |
| Scan de secrets (gitleaks) dans CI | ✅ | `.github/workflows/security.yml` |
| `.env.example` sans secrets réels | ✅ | Valeurs génériques uniquement |
| Aucun secret commité dans l'historique git | ✅ | Vérifié par validate.sh + gitleaks |
| SECURITY.md avec politique complète | ✅ | 5 principes, 6 règles GUARD, 4 vecteurs d'attaque |
| Politique de rotation des secrets documentée | ✅ | Runbooks dans DESCRIPTION.md |
| Fail-closed par défaut pour les erreurs de sécurité | ✅ | Règles GUARD-1 et GUARD-2 |

## 5. Documentation et conformité (Product Owner)

| Critère | Statut | Remarque |
|---|---|---|
| README.md avec installation, configuration, usage | ✅ | Badges CI inclus |
| CONSTITUTION.md complète (principes, forces, articles) | ✅ | 71 articles en 12 titres |
| DESCRIPTION.md complète (architecture, agents, skills) | ✅ | Architecture, agents, skills, cron, constitution |
| CHANGELOG.md à jour | ✅ | Dernière entrée : 2026-05-06 |
| SECURITY.md avec politique et runbooks | ✅ | Procédures d'urgence documentées |
| PRODUCTION_READY_CHECKLIST.md | ✅ | Ce fichier |
| `.env.example` avec toutes les variables documentées | ✅ | 34 variables avec descriptions |
| `openclaw.json.example` complet et commenté | ✅ | JSON5 avec sections gateway, channels, agents, cron |
| Licence identifiée | ✅ | Mentionnée dans README |
| Installation testable sur machine fraîche | ✅ | via `make install` ou `bash scripts/install.sh` |

---

## Résumé

| Domaine | Critères | ✅ |
|---|---|---|
| Architecture | 8 | 8 |
| Tests | 9 | 9 |
| CI/CD | 6 | 6 |
| Sécurité | 7 | 7 |
| Documentation | 10 | 10 |
| **Total** | **40** | **40** |

> Dernière mise à jour : 2026-05-06
