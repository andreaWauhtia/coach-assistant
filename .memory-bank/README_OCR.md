# Timeline SportEasy - Analyse des événements de match

## Vue d'ensemble

Cet outil permet d'analyser les événements d'un match en lisant les captures de la timeline SportEasy.

**Approche :** Lecture manuelle des images → Structuration en JSON → Classification automatique → Export CSV/Markdown

## Workflow rapide

### Étape 1 : Lire les événements des images
- Ouvrez les captures de la timeline SportEasy
- Lisez les événements manuellement (minute, type, joueur, position)
- Notez le header du match (équipes et score)

### Étape 2 : Créer un fichier JSON
Exemple :
```json
{
  "match_header": "R.St.FC.Bouillon 4-12 USAO U8 2025/2026",
  "events": [
    {"minute": 5, "type": "Tir arrêté", "player": "Lilou Douny", "side": "right"},
    {"minute": 4, "type": "But", "player": "Nestor Arnould", "side": "left"},
    {"minute": 3, "type": "Tir à côté", "player": "Nestor Arnould", "side": "left"}
  ]
}
```

### Étape 3 : Exécuter le parser
```bash
python tools/parse_timeline.py --input timeline.json --out-dir output
```

### Résultats
- **CSV** : `output/parsed_by_side.csv` — Tableau complet avec classifications
- **Markdown** : `output/{matchday}.md` — Rapport formaté

## Format d'entrée JSON

### match_header
Format : `"Équipe1 score1-score2 Équipe2 [saison]"`

Exemple :
- `"R.St.FC.Bouillon 4-12 USAO U8 2025/2026"` ✅
- `"Paris 2-1 Lyon 2024/2025"` ✅

**Important :** L'équipe de gauche est votre équipe (nous), celle de droite est l'adversaire.

### events[]
Tableau avec structure :
```json
{
  "minute": 45,
  "type": "But|Carton Jaune|Carton Rouge|Remplacement|Arrêt|Tir à côté|Poteau|Transversale|Tir arrêté|Blessé",
  "player": "Nom du Joueur ou null",
  "side": "left" ou "right"
}
```

## Sortie CSV : parsed_by_side.csv

| Colonne | Description |
|---------|-------------|
| `minute` | Minute du match |
| `type` | Type d'événement |
| `player` | Nom du joueur |
| `side` | Position sur timeline (left/right) |
| **`team`** | Équipe détectée (us/opponent) |
| **`classification`** | Catégorie (goal/shoot/card/substitution/injury) |
| **`inferred_actions`** | Actions déduites (frappe_créée/frappe_subite) |
| `confidence` | Confiance du parsing (0.0-1.0) |

### Classification automatique

**Shoots** (tous les tirs) :
- Tir à côté → shoot
- Poteau → shoot
- Transversale → shoot
- Arrêt → shoot
- Tir arrêté → shoot

**Inférences intelligentes** :

Si **NOUS** avons "Arrêt/Tir arrêté" → `frappe_subite`
(L'adversaire a tiré et nous avons défendu)

Si **ADVERSAIRE** a "Arrêt/Tir arrêté" → `frappe_créée`
(Nous avons tiré et l'adversaire a défendu)

## Modes d'utilisation

### Mode fichier (recommandé)
```bash
python tools/parse_timeline.py \
  --input timeline.json \
  --out-dir output \
  --matchday 2025-11-01
```

### Mode interactif
```bash
python tools/parse_timeline.py --interactive
```

Vous serez guidé pour entrer les données manuellement.

### Options disponibles
```
--input FILE          Fichier JSON avec les événements
--interactive, -I     Mode interactif (saisie manuelle)
--out-dir DIR         Dossier de sortie (défaut: .memory-bank/competitions)
--matchday ID         Identifiant du match (défaut: date du jour)
--our-team NAME       Nom de notre équipe (auto-détecté par défaut)
```

## Exemple complet

### Input : timeline.json
```json
{
  "match_header": "R.St.FC.Bouillon 4-12 USAO U8 2025/2026",
  "events": [
    {"minute": 90, "type": "Coup de sifflet final", "player": null, "side": null},
    {"minute": 85, "type": "But", "player": "Thomas Martin", "side": "right"},
    {"minute": 80, "type": "Arrêt", "player": "Jérôme Dupont", "side": "left"},
    {"minute": 75, "type": "Tir à côté", "player": "Nestor Arnould", "side": "left"},
    {"minute": 70, "type": "But", "player": "Nestor Arnould", "side": "left"}
  ]
}
```

### Commande
```bash
python tools/parse_timeline.py --input timeline.json --out-dir output --matchday "2025-11-01"
```

### Output : parsed_by_side.csv
```csv
minute,type,player,side,team,classification,inferred_actions,confidence
85,But,Thomas Martin,right,opponent,goal,,1.00
80,Arrêt,Jérôme Dupont,left,us,shoot,frappe_subite,1.00
75,Tir à côté,Nestor Arnould,left,us,shoot,,1.00
70,But,Nestor Arnould,left,us,goal,,1.00
```

### Output : 2025-11-01.md
```markdown
# Match: R.St.FC.Bouillon 4 - 12 USAO U8
*Généré le 2025-11-07 12:45:01*

## Résumé
- **R.St.FC.Bouillon**: 2 buts, 2 tirs
- **USAO U8**: 1 buts, 0 tirs

## Distribution temporelle (par tranche 5')

**70'-74'**: 1 événements
  - But (Nestor Arnould) [US]

**75'-79'**: 1 événements
  - Tir à côté (Nestor Arnould) [US]

**80'-84'**: 1 événements
  - Arrêt (Jérôme Dupont) [US]

**85'-89'**: 1 événements
  - But (Thomas Martin) [OPPONENT]

## Tous les événements
-  85' — But — Thomas Martin [OPPONENT] — goal
-  80' — Arrêt — Jérôme Dupont [US] — shoot (inféré: frappe_subite)
-  75' — Tir à côté — Nestor Arnould [US] — shoot
-  70' — But — Nestor Arnould [US] — goal
```

## Dépannage

### Le CSV est vide
- Vérifiez que le JSON est valide (utilisez `python -m json.tool timeline.json`)
- Vérifiez que le champ `events` contient des éléments

### Équipes mal détectées
- Vérifiez le format du header
- Format attendu : `"ÉquipeGauche score-score ÉquipeDroite [saison]"`
- Exemple : `"Paris 2-1 Lyon 2024/2025"` ✅

### Événements pas classifiés
- Vérifiez que le type d'événement est reconnu (liste à jour dans le script)
- Le script est insensible à la casse

## Fichiers de référence

- `GUIDE_PARSE_TIMELINE.md` — Documentation complète
- `example_timeline.json` — Exemple d'entrée
- `tools/parse_timeline.py` — Script principal

## Notes importantes

1. ✅ **Pas d'OCR requis** — Vous lisez les images vous-même
2. ✅ **Classification intelligente** — Le script déduit automatiquement les équipes et catégories
3. ✅ **Inférence métier** — Les "arrêts" deviennent des "frappes subies" ou "créées"
4. ✅ **Export flexible** — CSV pour Excel/analyse, Markdown pour rapport lisible
