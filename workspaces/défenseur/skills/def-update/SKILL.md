---
name: def-update
description: Gestion des mises à jour : veille CVE, niveaux d'urgence, procédure sécurisée (sauvegarde préalable).
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Gestion des mises à jour

## Veille hebdomadaire

Chaque lundi, après l'audit ANSSI :

1. `[N1]` Vérifier la version courante d'OpenClaw
2. `[N1]` Vérifier les releases disponibles (changelog)
3. `[N1]` Scanner les dépendances pour CVE connus (NVD/NIST)
4. `[N1]` Vérifier les versions de : Python, exchangelib, caldav, requests, et autres librairies actives
5. `[N2]` Produire un rapport de veille dans le REPORT `weekly`

## Niveaux d'urgence

| Scénario | Niveau | Délai de traitement |
|---|---|---|
| CVE critique (CVSS ≥ 9.0) sur une dépendance active | CRITIQUE | < 24h |
| CVE élevé (CVSS 7.0–8.9) | HAUT | < 7 jours |
| Mise à jour majeure OpenClaw disponible | MOYEN | < 30 jours |
| Mise à jour mineure ou patch | INFO | Prochaine fenêtre |

## Procédure de mise à jour sécurisée

**Toute mise à jour = sauvegarde préalable obligatoire.**

1. `[N3]` Confirmer avec l'utilisateur avant toute mise à jour majeure
2. `[N3]` Déclencher une sauvegarde complète via `def-backup`
3. `[N2]` Appliquer la mise à jour
4. `[N1]` Vérifier le fonctionnement : healthcheck `def-maintenance`
5. `[N1]` Relancer un audit `def-audit` post-mise à jour
6. `[N2]` Documenter en REPORT `weekly` ou `incident` selon le niveau d'urgence

Si la mise à jour échoue ou dégrade un service :
- Arrêt immédiat
- Restauration depuis la sauvegarde pré-mise à jour
- ALERT HAUT + REPORT `incident`

## Politique de version minimum

- Aucune librairie en version obsolète (fin de support > 6 mois) ne reste active.
- Aucun composant sans mise à jour de sécurité depuis 12 mois sans justification documentée.
- Les mises à jour critiques (CVSS ≥ 9.0) ne peuvent pas être reportées sans confirmation explicite.
