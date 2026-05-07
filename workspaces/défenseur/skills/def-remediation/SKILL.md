---
name: def-remediation
description: Runbooks d'incidents (5) : confinement, éradication, rétablissement. Exécute après DIAGNOSTIC validé.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Remédiation et correction

## Règle fondamentale

Aucune action de ce skill ne s'exécute sans un DIAGNOSTIC validé en entrée. Si le DIAGNOSTIC manque, le produire d'abord avec `def-defense`.

## Procédure générale (NIST SP 800-61 — Phase 3)

### Étape 1 — Confinement
1. Stopper la propagation sans détruire les preuves.
2. Isoler le service ou composant affecté si possible (niveau 3 — confirmation requise).
3. Préserver les logs avant toute modification.
4. Documenter l'état système à l'instant T.

### Étape 2 — Éradication
1. Identifier et supprimer la cause racine.
2. Vérifier l'absence de portes dérobées ou modifications non autorisées.
3. Nettoyer les artefacts (fichiers temporaires, entrées de log corrompues).
4. Toute suppression = niveau 3 = confirmation obligatoire.

### Étape 3 — Rétablissement
1. Restaurer depuis la dernière sauvegarde validée si nécessaire (`def-backup`).
2. Vérifier le fonctionnement de chaque service affecté.
3. Relancer un audit complet (`def-audit`).
4. Générer le REPORT `incident`.

---

## Runbooks d'incidents typiques

### RB-01 — Secret exposé dans un fichier versionné

**Gravité** : CRITIQUE 
**Déclencheur** : secret détecté dans git, log, rapport ou note Notion

1. `[N3]` Invalider immédiatement le secret compromis auprès du service concerné.
2. `[N3]` Générer un nouveau secret et mettre à jour `~/.openclaw/.env`.
3. `[N2]` Supprimer le secret de l'historique git (`git filter-repo` ou `BFG`).
4. `[N2]` Auditer les accès récents du service compromis.
5. `[N2]` Documenter en REPORT `incident` + dépôt Notion `[POST-MORTEM]`.

### RB-02 — Service principal indisponible

**Gravité** : HAUT 
**Déclencheur** : Telegram, Posteo, EWS ou Notion ne répond pas depuis > 15 min

1. `[N1]` Vérifier la connectivité réseau générale.
2. `[N1]` Vérifier le statut du service (page status officielle si disponible).
3. `[N2]` Journaliser l'indisponibilité avec timestamp de début.
4. `[N2]` Notifier l'utilisateur si Telegram est disponible, sinon attendre.
5. `[N2]` Relancer vérification toutes les 15 min jusqu'à rétablissement.
6. `[N2]` Générer REPORT `incident` si indisponibilité > 2h.

### RB-03 — Dérive de configuration détectée

**Gravité** : MOYEN à HAUT selon l'écart 
**Déclencheur** : `def-audit` détecte un écart par rapport à la configuration de référence

1. `[N1]` Identifier l'écart précis (fichier, paramètre, valeur attendue vs valeur actuelle).
2. `[N1]` Déterminer si l'écart est intentionnel (modification récente autorisée) ou non.
3. `[N2]` Produire un DIAGNOSTIC avec l'écart et son impact potentiel.
4. `[N3]` Proposer un ACTION_PLAN de correction si non intentionnel.
5. `[N2]` Après correction, relancer un audit ciblé pour valider.

### RB-04 — Échec de sauvegarde

**Gravité** : HAUT 
**Déclencheur** : sauvegarde quotidienne absente ou checksum invalide

1. `[N1]` Vérifier l'espace disque disponible sur la destination de sauvegarde.
2. `[N1]` Vérifier les permissions d'écriture sur `$BACKUP_DEST`.
3. `[N1]` Consulter les logs de la sauvegarde pour identifier l'erreur.
4. `[N3]` Relancer la sauvegarde manuellement après correction.
5. `[N2]` Journaliser la cause et la correction.
6. Si l'échec se répète 3 fois : ALERT CRITIQUE + demande de confirmation pour changer de destination.

### RB-05 — Tâche inter-agent bloquée

**Gravité** : MOYEN 
**Déclencheur** : tâche dans `~/.openclaw/shared/tasks/pending/` non traitée depuis > 24h

1. `[N1]` Identifier la tâche bloquée (fichier dans pending/ depuis > 24h).
2. `[N1]` Vérifier si l'agent cible (défenseur ou bâtisseur) est actif (health.json / bat-health.json).
3. `[N2]` Si l'agent cible est inactif : produire un DIAGNOSTIC.
4. `[N3]` Si la tâche n'est plus pertinente : la déplacer vers `done/` avec un résultat `cancelled`.
5. Si 3 tâches consécutives vers le même agent restent bloquées : ALERT HAUT + vérification de la configuration inter-agent.
