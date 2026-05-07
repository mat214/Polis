---
name: int-notion
description: Accès carnets Notion PERSO et SYNDICAL (notes, tâches, projets). Apprentissage de contexte.
metadata:
 {
  "openclaw":
   {
    "requires":
     { "env": ["NOTION_TOKEN", "NOTION_DB_PERSO_ID", "NOTION_DB_SYNDICAL_ID"] },
   },
 }
---

# Notion — espace personnel

## Carnets de notes configurés

| Variable | Carnet Notion | Contexte |
|---|---|---|
| `$NOTION_DB_PERSO_ID` | Carnet de notes perso | `[PERSO]` |
| `$NOTION_DB_SYNDICAL_ID` | Carnet de notes syndicat | `[SYNDICAL]` |

Toutes les valeurs sont lues depuis `~/.openclaw/.env`.
Token partagé : `$NOTION_TOKEN`.

> Le carnet "Carnet de notes openclaw" (`$NOTION_DB_OPENCLAW_ID`) est géré exclusivement
> par `shared-notion-openclaw`. Ce skill n'y accède pas.

## Connexion API

- API : Notion API v1 (`https://api.notion.com/v1`)
- Authentification : `Authorization: Bearer $NOTION_TOKEN`
- Version : `Notion-Version: 2022-06-28`
- **Rate limit** : 3 requêtes/seconde maximum — ne pas dépasser lors des triages et briefs.

## Schéma recommandé pour les deux carnets

Chaque entrée (tâche, projet ou note) est une **page** dans la database du carnet.
La propriété `Type` distingue le contenu au sein d'un même carnet.

| Propriété | Type Notion | Valeurs possibles | Obligatoire |
|---|---|---|---|
| `Titre` | title | — | Oui |
| `Type` | select | Tâche \| Projet \| Note | Oui |
| `Statut` | select | À faire \| En cours \| Terminé \| Bloqué | Oui (sauf Notes) |
| `Priorité` | select | Haute \| Normale \| Basse | Pour Tâches |
| `Échéance` | date | — | Pour Tâches et Projets |
| `Source` | select | Mail \| Telegram \| Manuel \| Agenda | Oui |
| `Créé le` | created_time | Auto | Auto |
| `Modifié le` | last_edited_time | Auto | Auto |

## Opérations

Les opérations s'appliquent identiquement aux deux carnets (PERSO et SYNDICAL).
Le carnet cible est déterminé par le contexte de l'action en cours.

### Tâches (Type = "Tâche")

| Opération | Niveau | Notes |
|---|---|---|
| Lister les tâches non terminées | 1 | Filtrer : `Type = Tâche` ET `Statut ≠ Terminé` |
| Lire le détail d'une tâche | 1 | — |
| Créer une tâche | 2 | — |
| Marquer une tâche comme terminée | 2 | — |
| Modifier priorité ou échéance | 2 | — |
| Supprimer / archiver une tâche | 3 | Confirmation obligatoire |

### Projets (Type = "Projet")

| Opération | Niveau | Notes |
|---|---|---|
| Lister les projets actifs | 1 | Filtrer : `Type = Projet` ET `Statut ≠ Terminé` |
| Lire une page projet | 1 | — |
| Créer un projet | 2 | Confirmation si contexte `[SYNDICAL]` |
| Modifier le statut d'un projet | 2 | — |
| Archiver un projet | 3 | Confirmation obligatoire |

### Notes (Type = "Note")

| Opération | Niveau | Notes |
|---|---|---|
| Lire, chercher des notes | 1 | — |
| Créer une note | 2 | — |
| Modifier une note existante | 3 | Confirmation obligatoire |
| Supprimer une note | 3 | Confirmation obligatoire |

## Requête API type (exemple : lister les tâches PERSO non terminées)

```python
response = notion.databases.query(
  database_id=NOTION_DB_PERSO_ID,
  filter={
    "and": [
      {"property": "Type", "select": {"equals": "Tâche"}},
      {"property": "Statut", "select": {"does_not_equal": "Terminé"}}
    ]
  },
  sorts=[{"property": "Échéance", "direction": "ascending"}],
  page_size=100
)
```

Si `has_more = true` dans la réponse : paginer via `start_cursor` jusqu'à épuisement.

---

## Détermination du contexte — apprentissage progressif

La détermination du contexte cible (`PERSO` ou `SYNDICAL`) est une **compétence qui s'affine avec le temps**.
L'agent part de signaux explicites, puis apprend à reconnaître des signaux implicites au fil des validations.

### Signaux de contexte (par ordre de priorité)

| Priorité | Signal | Exemple | Fiabilité |
|---|---|---|---|
| 1 | Source explicite (boite mail) | Mail reçu sur `syndical-b@exemple.org` → `[SYNDICAL]` | Certaine |
| 2 | Expéditeur connu en mémoire | Contact mémorisé comme syndical → `[SYNDICAL]` | Haute |
| 3 | Mots-clés dans le titre/sujet | "réunion FERC", "mandat", "confédérale" → `[SYNDICAL]` | Moyenne |
| 4 | Heure et fréquence | Lundi matin → souvent `[SYNDICAL]` (observé en mémoire) | Indicative |
| 5 | Aucun signal clair | → **Demander à l'utilisateur** | — |

### Règle fondamentale : en cas de doute, demander

Si aucun signal de priorité 1 ou 2 n'est présent et que les signaux restants sont contradictoires ou absents :

```
⚠️ Contexte incertain pour : "[titre de la tâche/note]"
Dans quel carnet dois-je l'enregistrer ?
→ [PERSO] Carnet de notes perso
→ [SYNDICAL] Carnet de notes syndicat
```

**Ne jamais deviner silencieusement.** Une erreur de contexte est difficile à détecter et peut entraîner
des croisements entre vie personnelle et activité syndicale.

### Cycle d'apprentissage du contexte

```
OBSERVATION (source + contenu + heure + expéditeur)
  │
  ▼
SIGNAL IDENTIFIÉ ?
  ├─ Oui (priorité 1-2) ──────────────────────→ Agir directement
  ├─ Oui (priorité 3-4, non contradictoire) ──→ Agir + proposer mémorisation
  └─ Non ou ambigu ───────────────────────────→ Demander confirmation
                           │
                           ▼
                        RÉPONSE UTILISATEUR
                           │
                           ▼
                      MÉMORISER le signal via `int-memory`
                      (après 3 validations du même signal → règle automatique)
```

### Mémorisation des signaux de contexte

Après validation par l'utilisateur, l'agent propose d'enregistrer le signal dans `int-memory` :

```
✅ Noté : j'ai enregistré "[Titre]" dans [CARNET].
Voudrais-tu que je retienne ce signal pour les prochaines fois ?
→ "Oui, retenir" | "Non, cas unique"
```

Exemples de signaux mémorisables :
- `"réunion bureau fédéral" → [SYNDICAL]` (observé 3x)
- Contact "Sophie D." → toujours `[SYNDICAL]`
- Tâches créées depuis Gmail le week-end → souvent `[PERSO]`

Une fois mémorisé, le signal passe en **priorité 2** et ne nécessite plus de confirmation.
L'agent signale quand il utilise un signal appris : `(contexte déterminé par apprentissage — signal mémorisé le [DATE])`.
