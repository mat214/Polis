# SECURITY — Politique de sécurité OpenClaw (Polis)

Ce fichier documente les règles de sécurité, les vecteurs d'attaque connus, et les procédures de signalement.
Ces règles sont une déclinaison opérationnelle de la [CONSTITUTION.md](./CONSTITUTION.md), Titres I et V.

---

## Principes fondamentaux

1. **Least Privilege** — chaque agent, skill et compte de service dispose des permissions minimales nécessaires à sa fonction.
2. **Fail-Closed** — en cas de doute ou d'erreur dans les systèmes de contrôle, l'action est bloquée par défaut.
3. **Human-in-the-Loop** — toute action irréversible requiert une confirmation humaine explicite avant exécution.
4. **Data Privacy by Design** — les données sensibles ne transitent jamais dans le session state, les logs de raisonnement, ou les contextes partagés.
5. **Immutable Audit Trail** — toute décision de la Guardrail Layer est enregistrée dans un log immutable.

---

## Guardrail Layer — Règles de gouvernance

La Guardrail Layer est un interceptor réel exécuté via `polis guardrail check` avant toute action `WRITE_SENSITIVE` ou `IRREVERSIBLE`. Logique implémentée dans `polis/guardrail/` (checker, rate limit SQLite, sanitization, Human Gate). Voir [`skills/shared-guardrail/SKILL.md`](./skills/shared-guardrail/SKILL.md) pour le protocole d'utilisation et [`polis/guardrail/`](./polis/guardrail/) pour le code.

**Règle GUARD-1 — Évaluation préventive**
Aucun skill de niveau `WRITE_SENSITIVE` ou `IRREVERSIBLE` ne s'exécute sans avoir traversé la Guardrail Layer. Contourner la couche constitue une violation critique de sécurité.

**Règle GUARD-2 — Fail-closed**
En cas d'erreur dans la Guardrail Layer elle-même (bug, timeout, indisponibilité), l'action est bloquée par défaut. Principe : *mieux vaut ne pas agir que d'agir sans contrôle*.

**Règle GUARD-3 — Toute décision est loggée**
Chaque évaluation produit une entrée de log structurée (action tentée, classification, décision PASS/BLOCK/GATE, timestamp, session_id) dans `~/.openclaw/guardrail.log`. Ces logs sont immutables.

**Règle GUARD-4 — Le dry-run ne remplace pas le gate**
Un dry-run réussi n'est pas une autorisation d'exécution. L'humain doit approuver explicitement après avoir vu le résultat simulé.

**Règle GUARD-5 — Pas d'auto-élévation**
Aucun agent ne peut modifier son propre niveau d'autorisation, désactiver la Guardrail Layer, ou approuver ses propres Human Gates.

**Règle GUARD-6 — Isolation des données externes**
Toute donnée provenant d'une source non contrôlée (web, email, fichier, API tierce) est marquée `[UNTRUSTED]` jusqu'à sanitization complète et ne peut pas modifier le contexte de raisonnement principal.

---

## Règles d'état (Session State)

**Règle STATE-1 — Sérialisation atomique**
Toute écriture dans le session state est atomique. Aucune écriture partielle.

**Règle STATE-2 — Immutabilité des étapes complétées**
Une étape marquée `done` ne peut pas être modifiée rétroactivement.

**Règle STATE-3 — Expiration obligatoire**
Toute session a une durée de vie maximale (`expires_at`). Une session expirée ne peut pas être réhydratée sans confirmation humaine.

**Règle STATE-4 — Isolation par agent**
Un agent ne peut lire ou écrire que dans ses propres sessions.

**Règle STATE-5 — Pas de données sensibles dans l'état**
Le session state stocke uniquement des références (UIDs, IDs), jamais le contenu des données sensibles.

---

## Vecteurs d'attaque connus

### Prompt Injection

Des contenus malveillants dans des emails, pages web, ou documents peuvent tenter de détourner le raisonnement de l'agent. Mitigations :
- Pipeline de sanitization (Chantier 3) détectant les patterns d'injection courants
- Isolation sémantique des données externes via balises `<external_content>`
- Troncature des données externes à 2000 tokens par source par step

### Skill Poisoning

Un skill malveillant installé sur l'instance peut exfiltrer des données ou exécuter des actions non autorisées. Mitigations :
- Tous les skills sont versionnés dans Git et revus manuellement avant intégration
- Les skills ne peuvent pas modifier leur propre descripteur d'autorisation en cours d'exécution
- Isolation des contextes par agent (Règle STATE-4)

### Runaway Loops

Un bug de raisonnement ou une tâche mal bornée peut entraîner l'agent dans une boucle infinie coûteuse. Mitigations :
- Rate limiting par skill (Chantier 3)
- Paramètre `max_steps` configurable par tâche
- Alerte et suspension automatique en cas de dépassement

### Credential Leakage

Les clés API et credentials ne doivent jamais apparaître dans les logs, le session state, ou les contextes LLM. Mitigations :
- Toutes les credentials dans `.env` (jamais committées — voir `.gitignore`)
- Les skills accèdent aux credentials via des variables d'environnement, pas via le contexte LLM
- Scan automatique des commits (recommandé : `gitleaks` en pre-commit hook)

---

## Signalement de vulnérabilités

Pour signaler une vulnérabilité de sécurité :

1. Ne pas ouvrir d'issue publique GitHub.
2. Contacter le mainteneur directement via le canal privé configuré sur l'instance.
3. Inclure : description de la vulnérabilité, étapes de reproduction, impact potentiel.
4. Délai de réponse cible : 48h.

---

## Dispositif d'isolation physique (recommandé)

Pour les instances gérant des données sensibles ou des actions à fort impact, il est recommandé de déployer OpenClaw sur un device dédié (machine physique séparée ou VM isolée), distinct de la machine principale de travail. Cela limite la surface d'attaque en cas de compromission de l'instance agent.

---

> Dernière mise à jour : 2026-05-06
