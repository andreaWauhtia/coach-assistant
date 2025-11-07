# Guide d'utilisation : Parse Timeline

## Vue d'ensemble

`tools/parse_timeline.py` traite les données **manuellement lues** de la timeline SportEasy et les classe automatiquement par équipe avec inférence intelligente des actions.

## Format d'entrée

Créez un fichier JSON avec la structure suivante :

```json
{
  "match_header": "R.St.FC.Bouillon 4-12 USAO U8 2025/2026",
  "events": [
    {
      "minute": 5,
      "type": "But",
      "player": "Nestor Arnould",
      "side": "left"
    },
    {
      "minute": 4,
      "type": "Tir arrêté",
      "player": "Lilou Douny",
      "side": "right"
    }
  ]
}
```

### Champs requis

- **`match_header`** : Format "Équipe1 score1-score2 Équipe2 [saison]"
  - L'équipe de gauche est votre équipe (côté "left")
  - L'équipe de droite est l'adversaire (côté "right")

- **`events[]`** : Tableau d'événements avec :
  - `minute` (int): Minute du match (1-90)
  - `type` (str): Type d'événement (voir liste ci-dessous)
  - `player` (str ou null): Nom du joueur
  - `side` (str): "left" (votre équipe) ou "right" (adversaire)

### Types d'événements reconnus

```
But                  → But marqué
Carton Jaune        → Carton jaune
Carton Rouge        → Carton rouge
Remplacement        → Changement de joueur
Arrêt               → Arrêt/tir contrôlé (→ shoot)
Tir à côté          → Tir à côté (→ shoot)
Poteau              → Tir sur le poteau (→ shoot)
Transversale        → Tir qui traverse (→ shoot)
Tir arrêté          → Tir arrêté (→ shoot)
Blessé              → Joueur blessé
```

## Utilisation

### Mode fichier (recommandé)

```bash
python tools/parse_timeline.py \
  --input timeline_data.json \
  --out-dir .memory-bank/competitions \
  --matchday "2025-11-01"
```

### Mode interactif

```bash
python tools/parse_timeline.py --interactive
```

Le script vous demandera d'entrer les données du match manuellement.

## Résultats

Le script génère deux fichiers :

### 1. `parsed_by_side.csv`

Tableau complet avec colonnes :
- `minute` : Minute du match
- `type` : Type d'événement
- `player` : Nom du joueur
- `side` : Côté (left/right)
- **`team`** : Équipe détectée (us / opponent)
- **`classification`** : Catégorie (goal / shoot / card / substitution / injury)
- **`inferred_actions`** : Actions déduites
  - `frappe_créée` : Nous avons tiré (l'adversaire a un arrêt)
  - `frappe_subite` : Nous avons subi une frappe (nous avons un arrêt)
- `confidence` : Confiance du parsing (0.0-1.0)

### 2. `{matchday}.md`

Rapport Markdown formaté avec :
- Résumé du match (buts, tirs par équipe)
- Distribution temporelle par tranche de 5 minutes
- Liste complète des événements avec classifications

## Logique intelligente

### Classification des shoots

Tous les événements suivants sont classifiés comme "shoot" :
- Tir à côté
- Poteau
- Transversale
- Arrêt
- Tir arrêté

### Inférence des frappes subies/créées

Le script déduit automatiquement :

**Si NOTRE ÉQUIPE a "Arrêt" ou "Tir arrêté"** :
→ `frappe_subite` (l'adversaire a tiré et nous avons défendu)

**Si l'ADVERSAIRE a "Arrêt" ou "Tir arrêté"** :
→ `frappe_créée` (nous avons tiré et l'adversaire a défendu)

## Exemple complet

Fichier d'entrée : `timeline.json`
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

Commande :
```bash
python tools/parse_timeline.py --input timeline.json --out-dir output
```

Résultat CSV :
```
minute,type,player,side,team,classification,inferred_actions,confidence
5,Tir arrêté,Lilou Douny,right,opponent,shoot,frappe_créée,1.00
4,But,Nestor Arnould,left,us,goal,,1.00
3,Tir à côté,Nestor Arnould,left,us,shoot,,1.00
```

Interprétation :
- ✅ Notre équipe a marqué 1 but (Arnould à 4')
- ✅ Notre équipe a tiré 2 fois (1 but, 1 à côté)
- ✅ L'adversaire a tiré 1 fois (arrêt à 5') → nous avons subi une frappe
- 💡 Score final : nous 4, adversaire 12 (match perdu mais on a tenté!)

## Notes importantes

1. Le header détermine **automatiquement** qui est "us" et qui est "opponent"
   - Équipe de gauche (team1) = notre équipe
   - Équipe de droite (team2) = adversaire

2. L'ordre des équipes dans le header est important !
   - Format correct : `NotreÉquipe score-score AdvEqu year`

3. La colonne `side` ("left"/"right") doit correspondre à la position sur la timeline

4. Les événements sans type d'action reconnu seront ignorés lors de la classification

## Dépannage

### CSV vide ou mal formaté

Vérifiez que le JSON est valide :
```bash
python -m json.tool timeline.json
```

### Équipes mal détectées

Vérifiez le format du header :
```
✅ Correct   : "R.St.FC.Bouillon 4-12 USAO U8 2025/2026"
❌ Incorrect : "R.St.FC.Bouillon-USAO U8 4-12"
```

### Événements pas classifiés

Vérifiez que le type est dans la liste reconnue. Le script est insensible à la casse ("But" = "but" = "BUT").
