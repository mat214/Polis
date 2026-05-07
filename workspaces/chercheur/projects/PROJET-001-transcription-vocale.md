# Transcription de notes vocales Telegram en journal structuré

**ID** : PROJET-001
**Statut** : proposé
**Urgence** : haute
**Créé le** : 2026-05-06
**Source** : veille — cas d'usage haute-technologie.fr

## Description

Permettre à l'utilisateur d'envoyer un message vocal Telegram à l'agent PA et d'obtenir une transcription structurée en journal quotidien. Le message vocal est transcrit via Whisper (modèle local), nettoyé (suppression des hésitations, ponctuation), et organisé en sections thématiques (travail, famille, santé, idées, vigilance).

## Dépendances OpenClaw

- **Agent cible** : intendant
- **Skills requis** : int-telegram (existant) → extension pour gérer les messages vocaux
- **Skills à créer** : int-voice-notes (traitement transcription, structuration, stockage)
- **Capacités système** : Whisper (modèle STT local), ffmpeg (conversion audio)

## Architecture proposée

```
Message vocal Telegram
  │
  ▼
int-telegram (extension) ── télécharge via Telegram API
  │
  ▼
bâtisseur (bat-capabilities) ── provisionne Whisper + ffmpeg
  │
  ▼
int-voice-notes (nouveau skill) ── pipeline transcription
  ├── 1. Conversion audio (ffmpeg)
  ├── 2. Transcription (Whisper local)
  ├── 3. Nettoyage / structuration
  └── 4. Persistance dans Notion via int-notion
```

## Indications techniques

- Whisper s'installe via `pip install openai-whisper` dans le venv `/opt/openclaw/venv/`
- Le modèle `base` ou `small` est suffisant (bon équilibre qualité/ressources)
- L'API Telegram expose `getFile` + `downloadFile` pour les messages vocaux (format OGG)
- `ffmpeg` nécessaire pour la conversion OGG → WAV (entrée Whisper)
- `bâtisseur` peut provisionner le tout via `bat-capabilities` (classification S pour ffmpeg + Whisper)
- Stockage : Notion via int-notion existant, + fichier local chiffré
- Sécurité : fichier audio supprimé après transcription, pas de synchronisation cloud

## Journal

- 2026-05-06 : Création — source : article haute-technologie.fr cas #3
