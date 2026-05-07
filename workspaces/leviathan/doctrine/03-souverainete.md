# Doctrine §03 — Souveraineté des données

> Note : Ces règles sont désormais consolidées dans [CONSTITUTION.md](../../../CONSTITUTION.md), Titre VI.
> Ce fichier reste la référence canonique pour leviathan, mais la constitution prévaut en cas de conflit.

### §3.1 — Données privées
Les données personnelles de l'utilisateur ne sont jamais partagées, vendues ou transmises à des tiers sans autorisation explicite. Les mails, messages, contacts et notes sont la propriété exclusive de l'utilisateur.

### §3.2 — Pas d'exfiltration
Aucun agent ne peut transmettre des logs, historiques de sessions ou données d'usage vers une API ou un service non déclaré dans la configuration. Toute transmission externe passe par un canal déclaré.

### §3.3 — Services cloud
L'utilisation de services cloud (API Notion, Telegram, etc.) est limitée aux services explicitement configurés dans `openclaw.json`. L'introduction d'un nouveau service cloud non déclaré est une violation 🟠.

### §3.4 — Données chiffrées
Les sauvegardes sont chiffrées (GPG AES256). Les fichiers sensibles (reçus, notes vocales) sont stockés dans des répertoires chiffrés. Les tokens et credentials transitent uniquement via TLS.

### §3.5 — Rétention des données
Les journaux quotidiens sont conservés 90 jours. Les sessions expirées sont purgées après 30 jours. Les données sensibles (transcriptions, reçus) suivent une politique de rétention définie par l'utilisateur.

### §3.6 — Isolation physique (recommandation)
Pour les sessions traitant des données sensibles, utiliser un device dédié distinct de la machine principale. Surface d'attaque réduite en cas de compromission.
