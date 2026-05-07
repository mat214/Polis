---
name: def-maintenance
description: Maintenance courante : nettoyage logs, healthcheck services, rotation secrets, rapports daily/weekly/monthly.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Maintenance courante

## Tâches quotidiennes

| Tâche | Niveau | Sortie |
|---|---|---|
| Vérification état des services (Telegram, Posteo, EWS, Notion) | N1 | Log + alerte si KO |
| Vérification présence de la sauvegarde du jour | N1 | Log |
| Scan rapide des logs pour anomalies évidentes | N1 | Log |
| Génération du REPORT `daily` | N2 | Notion `[RAPPORT-QUOTIDIEN]` |
| Vérification que les tâches planifiées ont bien tourné | N1 | Log |
| Validation technique feedbacks en attente (shared/feedback/) — réponse < 4h | N1 | Log |
| Remédiation feedbacks causant dysfonctionnement si détecté (FEED-4) | N2 | Log + alerte utilisateur |

## Tâches hebdomadaires (lundi matin)

| Tâche | Niveau | Sortie |
|---|---|---|
| Audit complet ANSSI (42 mesures) | N1 | REPORT `weekly` + score |
| Vérification des mises à jour disponibles | N1 | Log + proposition si nécessaire |
| Nettoyage des logs anciens (> 30 jours) | N2 | Log |
| Vérification de la rétention des sauvegardes | N1 | Log |
| Test de lisibilité de la dernière sauvegarde | N1 | Log |
| Proposition de révision mémoire (déléguer à l'intendant) | N2 | Message Telegram |
| Validation technique propositions de skills en attente (shared/skill_proposals/) — réponse < 24h | N1 | Log |
| Bilan post-déploiement des skills déployés depuis < 7 jours | N1 | Log |

## Tâches mensuelles

| Tâche | Niveau | Sortie |
|---|---|---|
| Test de restauration depuis sauvegarde | N3 | REPORT + confirmation |
| Rotation préventive des secrets si non modifiés depuis 90j | N3 | Log + confirmation |
| Audit de la politique de mémoire longue | N1 | Rapport à l'utilisateur |

## Rotation des logs

- Conservation : 30 jours pour les logs quotidiens, 1 an pour les logs d'incident.
- Format de nommage : `YYYY-MM-DD_[AGENT]_[TYPE].log`
- Les logs sont stockés dans `~/.openclaw/logs/` (jamais versionnés).
- Avant suppression d'un log : vérifier qu'il n'est pas lié à un incident ouvert.

## Healthcheck des services

Pour chaque service, vérifier :
1. **Telegram** : ping au bot, réponse < 5s
2. **Posteo IMAP** : connexion SSL sur port 993
3. **Posteo CalDAV/CardDAV** : connexion HTTPS
4. **EWS ORG-2** : autodiscovery + connexion
5. **Notion API** : appel `GET /users/me`, status 200

Résultat attendu : `[OK]` ou `[KO — raison]` pour chaque service.

## Format du rapport de maintenance

```
[MAINTENANCE][TIMESTAMP][défenseur]
Services  : <n>/5 OK
Sauvegarde : OK | ABSENTE | CORROMPUE
Logs    : nettoyés jusqu'à [date]
Anomalies  : <n>
Actions N2 : <liste>
Prochain audit complet : <date>
```
