---
name: def-backup
description: Sauvegarde et restauration : périmètre, chiffrement AES256, vérification intégrité, rétention, test mensuel.
metadata:
 {
  "openclaw":
   {
    "requires":
     { "env": ["BACKUP_DEST", "BACKUP_GPG_PASSPHRASE"], "bins": ["gpg"] },
   },
 }
---

# Sauvegarde et restauration

## Périmètre de sauvegarde

| Dossier | Contenu | Fréquence |
|---|---|---|
| `~/.openclaw/` | Config, skills, mémoire longue, workspaces | Quotidien |
| `~/.openclaw/logs/` | Logs des agents | Quotidien |
| `agents/` | Définitions des agents et leurs skills | Quotidien |

Exclusions : `.env` (jamais sauvegardé tel quel), fichiers temporaires, caches.

## Procédure de sauvegarde

1. `[N2]` Créer une archive compressée : `openclaw-backup-YYYY-MM-DD.tar.gz`
2. `[N2]` Chiffrer l'archive : `gpg --symmetric --cipher-algo AES256`
3. `[N2]` Calculer le checksum SHA256 de l'archive chiffrée
4. `[N2]` Copier vers `$BACKUP_DEST` (défini dans `.env`)
5. `[N2]` Journaliser : nom de fichier, taille, checksum, timestamp, destination
6. `[N1]` Vérifier la présence du fichier sur `$BACKUP_DEST`

Si une étape échoue : ALERT HAUT + arrêt de la procédure.

## Rétention

| Type | Durée de rétention |
|---|---|
| Sauvegardes quotidiennes | 7 jours |
| Sauvegardes hebdomadaires (lundi) | 4 semaines |
| Sauvegardes mensuelles (1er du mois) | 3 mois |

Les sauvegardes plus anciennes sont supprimées après confirmation (N3).

## Procédure de restauration

**Toujours une action de niveau 3 — confirmation obligatoire.**

1. `[N1]` Identifier la sauvegarde cible (date, checksum)
2. `[N1]` Vérifier l'intégrité : recalculer le SHA256 et comparer
3. `[N3]` Déchiffrer et décompresser dans un dossier temporaire
4. `[N3]` Comparer avec la version actuelle avant remplacement
5. `[N3]` Remplacer les fichiers concernés après confirmation
6. `[N2]` Relancer un audit `def-audit` pour valider l'état post-restauration
7. `[N2]` Documenter en REPORT `incident` si la restauration fait suite à un incident

## Variables d'environnement requises

```
BACKUP_DEST=    # destination : chemin local, NAS, ou cloud (ex: /mnt/nas/openclaw-backups)
BACKUP_GPG_PASSPHRASE= # passphrase de chiffrement (jamais dans les logs)
```

## Test mensuel de restauration

Chaque 1er lundi du mois :
1. Sélectionner la sauvegarde hebdomadaire la plus récente
2. La restaurer dans un dossier de test isolé
3. Vérifier que les fichiers clés sont lisibles et complets
4. Journaliser le résultat du test
5. Si le test échoue : ALERT CRITIQUE immédiate
