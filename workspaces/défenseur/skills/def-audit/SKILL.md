---
name: def-audit
description: Audit d'instance : configuration, permissions, secrets, services. ANSSI 42 mesures + CIS Level 1. REPORT avec score.
metadata:
 {
  "openclaw": { "always": true },
 }
---

# Audit de l'instance

## Quand charger ce skill

- Audit quotidien planifié
- Audit hebdomadaire complet
- Après une modification de configuration
- Sur demande explicite
- Après tout bootstrap avec anomalie détectée

## Périmètre d'audit

| Zone | Éléments vérifiés |
|---|---|
| Configuration | `openclaw.json`, workspaces `AGENTS.md`, `skills/` |
| Cohérence documentaire | `validate.sh` (0 erreur), agents config vs docs vs scripts, workspace files complets, constitution référencée |
| Secrets | Présence de secrets dans les fichiers versionés, logs, mémoire |
| Permissions | Droits des sous-agents, périmètres, allowlists |
| Services | État des connexions (Posteo, EWS, Notion, Telegram) |
| Sauvegardes | Dernière sauvegarde, intégrité, rétention |
| Dépendances | Versions d'OpenClaw et librairies, CVE connus |
| Logs | Présence, rotation, absence de secrets dans les entrées |

---

## Checklist ANSSI — 42 mesures d'hygiène informatique

Chaque mesure est vérifiée lors de l'audit hebdomadaire complet. 
L'audit quotidien couvre les mesures marquées `[QUOTIDIEN]`.

### Chapitre 1 — Connaître le système d'information
- [ ] R01 Dresser un inventaire exhaustif des composants du SI `[QUOTIDIEN]`
- [ ] R02 Maintenir un schéma du réseau à jour
- [ ] R03 Identifier les données sensibles et leur localisation

### Chapitre 2 — Maîtriser le réseau
- [ ] R04 Limiter les flux réseau aux seuls flux nécessaires
- [ ] R05 Sécuriser les accès Wi-Fi
- [ ] R06 Cloisonner les réseaux entre eux
- [ ] R07 Éviter l'exposition directe sur Internet des services sensibles

### Chapitre 3 — Maîtriser les identités et les accès
- [ ] R08 Identifier nommément chaque personne accédant au système `[QUOTIDIEN]`
- [ ] R09 Authentifier les utilisateurs avant tout accès `[QUOTIDIEN]`
- [ ] R10 Définir et vérifier des règles de robustesse des mots de passe `[QUOTIDIEN]`
- [ ] R11 Privilégier l'utilisation de l'authentification forte (MFA) `[QUOTIDIEN]`
- [ ] R12 Protéger les mots de passe stockés `[QUOTIDIEN]`
- [ ] R13 Bannir les comptes partagés
- [ ] R14 Restreindre les droits d'administration
- [ ] R15 Définir et appliquer le principe de moindre privilège `[QUOTIDIEN]`
- [ ] R16 Tracer les accès à distance et aux ressources sensibles `[QUOTIDIEN]`

### Chapitre 4 — Gérer le parc informatique
- [ ] R17 Inventorier et gérer les actifs matériels
- [ ] R18 Mettre à jour régulièrement les logiciels `[QUOTIDIEN]`
- [ ] R19 Activer les mises à jour automatiques si possible
- [ ] R20 Utiliser des logiciels maintenus et éviter les versions obsolètes
- [ ] R21 Protéger physiquement les équipements

### Chapitre 5 — Configurer et durcir les systèmes
- [ ] R22 Désactiver les services et ports inutilisés `[QUOTIDIEN]`
- [ ] R23 Chiffrer les données sensibles au repos et en transit `[QUOTIDIEN]`
- [ ] R24 Utiliser des protocoles sécurisés (TLS 1.2+, SSH, HTTPS) `[QUOTIDIEN]`
- [ ] R25 Durcir la configuration des services exposés
- [ ] R26 Configurer un pare-feu local
- [ ] R27 Activer la journalisation des événements de sécurité `[QUOTIDIEN]`

### Chapitre 6 — Protéger les données
- [ ] R28 Sauvegarder régulièrement les données essentielles `[QUOTIDIEN]`
- [ ] R29 Tester les procédures de restauration
- [ ] R30 Chiffrer les sauvegardes
- [ ] R31 Conserver une copie hors ligne ou hors site

### Chapitre 7 — Protéger la messagerie
- [ ] R32 Sensibiliser aux risques de phishing et ingénierie sociale
- [ ] R33 Filtrer les pièces jointes et liens suspects
- [ ] R34 Utiliser SPF, DKIM, DMARC pour l'envoi de mails
- [ ] R35 Ne pas cliquer sur les liens dans les mails non sollicités

### Chapitre 8 — Superviser et auditer
- [ ] R36 Centraliser et conserver les journaux `[QUOTIDIEN]`
- [ ] R37 Surveiller les journaux d'événements de sécurité `[QUOTIDIEN]`
- [ ] R38 Définir et tester une procédure de gestion des incidents
- [ ] R39 Effectuer des audits réguliers de configuration

### Chapitre 9 — Sensibiliser et organiser
- [ ] R40 Former et sensibiliser les utilisateurs aux bonnes pratiques
- [ ] R41 Définir une politique de sécurité formalisée
- [ ] R42 Désigner un responsable de la sécurité et de la gestion des incidents

---

## Checklist CIS Benchmark Level 1 — Linux (20 contrôles pratiques)

Vérifiés lors de l'audit hebdomadaire. Marqués `[QUOTIDIEN]` si critiques.

### Système de fichiers
- [ ] CIS-01 Partitions séparées pour `/tmp`, `/var`, `/home` si possible
- [ ] CIS-02 Option `noexec` sur `/tmp` et `/dev/shm`
- [ ] CIS-03 Permissions de `~/.openclaw/` : 700 (aucun accès groupe/autres) `[QUOTIDIEN]`
- [ ] CIS-04 Permissions de `~/.openclaw/.env` : 600 `[QUOTIDIEN]`
- [ ] CIS-05 Aucun fichier avec bit SUID/SGID inattendu dans le répertoire de l'agent

### Accès SSH
- [ ] CIS-06 Connexion root par SSH désactivée (`PermitRootLogin no`)
- [ ] CIS-07 Authentification par mot de passe SSH désactivée (`PasswordAuthentication no`)
- [ ] CIS-08 Version du protocole SSH : SSH2 uniquement
- [ ] CIS-09 Timeout de session inactive défini (`ClientAliveInterval ≤ 300`)
- [ ] CIS-10 Accès SSH limité aux utilisateurs autorisés (`AllowUsers`)

### Services et ports
- [ ] CIS-11 Aucun service inutilisé actif (vérifier avec `ss -tlnp` ou `netstat`) `[QUOTIDIEN]`
- [ ] CIS-12 Pare-feu actif (iptables ou ufw) avec politique par défaut DROP `[QUOTIDIEN]`
- [ ] CIS-13 Seuls les ports 22 (SSH), 443 (HTTPS sortant) et nécessaires aux agents sont ouverts

### Comptes et authentification
- [ ] CIS-14 Aucun compte sans mot de passe (`awk -F: '($2=="")' /etc/shadow`)
- [ ] CIS-15 Comptes inutilisés depuis > 90 jours désactivés
- [ ] CIS-16 Politique de mot de passe : longueur ≥ 14 caractères, expiration ≤ 365 jours

### Journalisation et intégrité
- [ ] CIS-17 `auditd` ou équivalent actif et configuré pour logger les appels système critiques `[QUOTIDIEN]`
- [ ] CIS-18 Rotation des logs système configurée (`logrotate`)
- [ ] CIS-19 Outil de contrôle d'intégrité des fichiers actif (AIDE, Tripwire ou équivalent)
- [ ] CIS-20 Synchronisation de l'horloge système (NTP/chrony) `[QUOTIDIEN]`

---

## Calcul du score de conformité

```
Score ANSSI = (mesures ANSSI conformes / 42) * 100
Score CIS  = (contrôles CIS conformes / 20) * 100
Score global = (ANSSI * 0.6) + (CIS * 0.4)

Objectif minimum : score global ≥ 80%
Seuil d'alerte  : score global < 70% → ALERT HAUT
Seuil critique  : score global < 50% → ALERT CRITIQUE
```

## Sortie attendue

Après chaque audit, générer un REPORT (format `shared-reporting`) avec :
- Score ANSSI + Score CIS + Score global
- Liste des écarts avec priorité de correction
- Recommandations classifiées HAUTE/MOYENNE/BASSE
- Dépôt Notion avec préfixe `[AUDIT]`
