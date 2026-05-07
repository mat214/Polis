# HEARTBEAT.md — défenseur

## Continu (toutes les heures)
- [ ] Vérification IOC : connexions réseau, processus, logs auth, intégrité fichiers

## Quotidien
- [ ] Bootstrap : environnement, services, sauvegardes, intégrité configuration
- [ ] Audit rapide : dérive de configuration, scan de secrets
- [ ] Générer REPORT daily → Notion OPENCLAW
- [ ] Vérifier l'exécution des tâches planifiées
- [ ] Écrire `health.json` dans `~/.openclaw/shared/`

## Hebdomadaire (lundi)
- [ ] Audit complet ANSSI (42 mesures) + CIS (20 contrôles)
- [ ] Exécuter `validate.sh` depuis le dépôt — 0 erreur, rapporter les écarts
- [ ] Cohérence documentaire : nombre d'agents identique dans config, docs et scripts
- [ ] Scan CVE : dépendances, librairies
- [ ] Nettoyage des logs (> 30 jours)
- [ ] Vérification de la rétention des sauvegardes
- [ ] Révision mémoire : relire les journaux quotidiens, mettre à jour MEMORY.md

## Mensuel (premier lundi)
- [ ] Test de restauration depuis une sauvegarde
- [ ] Rotation préventive des secrets si > 90 jours
- [ ] Audit de la politique de mémoire
