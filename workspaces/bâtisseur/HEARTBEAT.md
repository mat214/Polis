# HEARTBEAT.md — bâtisseur

## Quotidien (02h00)
- [ ] Audit système : paquets, services, ressources, intégrité des scripts
- [ ] Calculer le score de santé (0-100)
- [ ] Écrire `bat-health.json` dans `~/.openclaw/shared/`
- [ ] Scanne `~/.openclaw/shared/tasks/` pour les tâches bâtisseur en attente
- [ ] Générer le rapport quotidien → Notion OPENCLAW (02h30)
- [ ] Nettoyer `/tmp/openclaw-test/`

## Hebdomadaire (lundi 01h00)
- [ ] Vérifier les mises à jour de sécurité apt
- [ ] Vérification complète de l'intégrité des scripts (SHA256 vs git HEAD)
- [ ] Inventaire des crons
- [ ] Vérification des permissions (`/opt/openclaw/` 750, `.env` 600)
- [ ] Révision mémoire : relire les journaux quotidiens, mettre à jour MEMORY.md
