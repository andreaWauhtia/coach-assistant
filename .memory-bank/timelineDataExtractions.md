# Timeline SportEasy - Extraction et Traitement des Données

## Vue d'ensemble

Ce document décrit le processus complet d'extraction des données de timeline SportEasy, de la capture d'écran à l'analyse structurée en CSV et Markdown.

## 1. Structure de la Timeline SportEasy

### Disposition physique
```
┌─────────────────────────────────────────┐
│ Match: TEAM_HOME score - score TEAM_AWAY│
├─────────────┬───────────────┬───────────┤
│  TEAM_HOME  │  TIMELINE +   │ TEAM_AWAY │
│   (LEFT)    │ MINUTE MARKS  │  (RIGHT)  │
├─────────────┼───────────────┼───────────┤
│  Events     │    0' 5' 10'  │  Events   │
│  side:left  │   15' 20' ... │ side:right│
└─────────────┴───────────────┴───────────┘
```

### Convention d'interprétation des événements

**⚠️ IMPORTANT** : USAO U8 peut être à gauche (HOME) OU à droite (AWAY).

**Le système détecte automatiquement** :
1. Extraction du nom d'équipe depuis le header (ex: "R.St.FC.Bouillon 4-12 USAO U8")
2. Détermination du côté de USAO U8 (left = HOME, right = AWAY)
3. Utilisation du paramètre `--our-team "USAO U8"` lors du parsing

**Cas 1 : USAO U8 à DROITE (AWAY)** :
- `But` (right) → but marqué ✅
- `Tir à côté` (right) → tir hors cadre
- `Tir arrêté` (right) → tir cadré arrêté
- `Arrêt` (right) → gardien adverse a arrêté notre tir

**Cas 2 : USAO U8 à GAUCHE (HOME)** :
- `But` (left) → but marqué ✅
- `Tir à côté` (left) → tir hors cadre
- `Tir arrêté` (left) → tir cadré arrêté
- `Arrêt` (left) → gardien adverse a arrêté notre tir

**Pour l'équipe adverse** (quel que soit le côté) :
- `But` (adversaire) → but concédé ⚠️
- `Tir à côté` (adversaire) → tir hors cadre concédé
- `Tir arrêté` (adversaire) → tir cadré concédé
- `Arrêt` (adversaire) → **INFÉRÉ** : frappe créée (nous avons tiré, l'adversaire a arrêté)

## 2. Processus d'extraction manuelle des captures d'écran

### Étape 1 : Lecture des images
1. Examiner chaque capture d'écran de haut en bas (sens chronologique)
2. Identifier la minute de chaque événement (centrée sur l'axe)
3. Déterminer le côté de l'événement (left = HOME/adversaire, right = AWAY/nous)
4. Lire le type d'événement (But, Tir arrêté, Arrêt, etc.)
5. Lire le nom du joueur (si visible)

### Étape 2 : Structuration en JSON
```json
{
  "match_header": "R.St.FC.Bouillon 4-12 USAO U8 2025/2026",
  "match_date": "2025-11-01",
  "structure": "HOME (left) | TIMELINE | AWAY (right). USAO U8 peut être à gauche OU à droite",
  "events": [
    {
      "minute": 2,
      "type": "Tir à côté",
      "player": "Nestor Arnould",
      "side": "right"
    },
    {
      "minute": 12,
      "type": "Tir à côté",
      "player": "adversaire",
      "side": "left"
    }
  ]
}
```

**Format du fichier** : `match_{DATE}_{AWAY_TEAM}.json` ou `match_{DATE}_{HOME_TEAM}.json`
- Exemple (USAO AWAY) : `match_2025-11-01_usao_clean.json`
- Exemple (USAO HOME) : `match_2025-10-15_usao_home.json`
- Localisation : `/workspaces/mystuff/`

**Le header est crucial** : Il détermine automatiquement qui est HOME/AWAY
- Format reconnu : `"TEAM_HOME score-score TEAM_AWAY"` ou `"TEAM_HOME score-score TEAM_AWAY season"`
- Exemples valides :
  - `"R.St.FC.Bouillon 4-12 USAO U8 2025/2026"` → HOME=Bouillon, AWAY=USAO
  - `"USAO U8 10-3 FC Truc 2025/2026"` → HOME=USAO, AWAY=FC Truc


### Étape 3 : Points d'attention
- Si un joueur n'est pas identifiable : utiliser `"player": "adversaire"` (pour left) ou `"player": "unknown"`
- Utiliser l'heure exacte de la capture (ex. 2' pour 2 minutes)
- Classer les événements dans l'ordre temporel

## 3. Pipeline de traitement (parse_timeline.py)

### Architecture du script
```
INPUT: match_*.json
  ↓
[1] load_events_from_json()
    └─ Charge le JSON structuré
  ↓
[2] parse_header()
    └─ Extrait : team1 (HOME), team2 (AWAY), score1, score2
  ↓
[3] classify_and_enrich_events()
    ├─ Assigne team: "us" (right) ou "opponent" (left)
    ├─ Classe par type : goal, shoot, substitution, card, injury
    └─ Infère frappe_subite/frappe_créée sur Arrêt/Tir arrêté
  ↓
[4] export_to_csv()
    └─ Génère parsed_by_side.csv
  ↓
[5] build_report()
    └─ Génère {matchday}.md (Markdown)
  ↓
OUTPUT: ./{out_dir}/
  ├─ parsed_by_side.csv
  └─ {matchday}.md
```

### Logique de classification des équipes
```python
# SportEasy layout: HOME (left) | TIMELINE | AWAY (right)
if side == 'left':
    team = 'opponent'  # HOME team
elif side == 'right':
    team = 'us'        # AWAY team (our perspective)
```

### Inférence d'actions implicites
```python
# Quand notre équipe (right) a un Arrêt/Tir arrêté
if team == 'us' and event_type in ('Arrêt', 'Tir arrêté'):
    inferred_actions.append('frappe_subite')  # adversaire a tiré
    # = l'adversaire a tiré sur nous

# Quand l'adversaire (left) a un Arrêt/Tir arrêté
if team == 'opponent' and event_type in ('Arrêt', 'Tir arrêté'):
    inferred_actions.append('frappe_créée')  # nous avons tiré
    # = nous avons tiré et l'adversaire a arrêté
```

## 4. Exécution du pipeline

### Commande de base
```bash
cd /workspaces/mystuff
python tools/parse_timeline.py \
  --input match_usao_clean.json \
  --out-dir analysis_final_clean \
  --matchday "2025-11-01_USAO_vs_Bouillon" \
  --our-team "USAO U8"
```

### Paramètres
- `--input` : Chemin au fichier JSON (requis)
- `--out-dir` : Répertoire de sortie (défaut : `.`)
- `--matchday` : Identifiant du match au format `YYYY-MM-DD_TEAM` (défaut : date du jour)
- `--our-team` : Nom de notre équipe (optionnel, pour validation)

### Sortie générée
```
analysis_final_clean/
├── parsed_by_side.csv           # Données brutes structurées
└── 2025-11-01_USAO_vs_Bouillon.md  # Rapport formaté
```

## 5. Structure du CSV de sortie

**Colonnes** : `minute`, `type`, `player`, `side`, `team`, `classification`, `inferred_actions`, `confidence`

**Exemple** :
```csv
minute,type,player,side,team,classification,inferred_actions,confidence
2,Tir à côté,Nestor Arnould,right,us,shoot,,1.00
5,Tir arrêté,Lilou Douny,right,us,shoot,frappe_subite,1.00
12,Tir à côté,adversaire,left,opponent,shoot,,1.00
34,Arrêt,adversaire,left,opponent,shoot,frappe_créée,1.00
```

## 6. Structure du Markdown de sortie

**Sections** :
1. **Titre** : `# Match: TEAM1 score1 - score2 TEAM2`
2. **Résumé** : Statistiques globales (buts, tirs)
3. **Distribution temporelle** : Événements groupés par tranches de 5'
4. **Tous les événements** : Liste complète avec classifications

**Exemple** :
```markdown
# Match: R.St.FC.Bouillon 4 - 12 USAO U8

## Résumé
- **R.St.FC.Bouillon**: 4 buts, 3 tirs
- **USAO U8**: 12 buts, 6 tirs

## Distribution temporelle (par tranche 5')

**0'-4'**: 5 événements
  - Tir à côté (Nestor Arnould) [US]
  - But (Nestor Arnould) [US]
  ...

## Tous les événements
-  2' — Tir à côté — Nestor Arnould [US] — shoot
-  4' — But — Nestor Arnould [US] — goal
  ...
```

## 7. Sauvegarde et archivage

### Localisation des outputs
- **Fichier JSON source** : `/workspaces/mystuff/match_*.json`
- **CSV généré** : `/workspaces/mystuff/analysis_*/parsed_by_side.csv`
- **Rapport Markdown** : `/workspaces/mystuff/analysis_*/{matchday}.md`

### Archive dans .memory-bank (optionnel)
Pour conserver l'analyse pour comparaisons ultérieures :
```bash
mkdir -p .memory-bank/competitions
cp analysis_final_clean/2025-11-01_USAO_vs_Bouillon.md \
   .memory-bank/competitions/2025-11-01_USAO_vs_Bouillon.md
```

## 8. Métriques calculées

### À partir du CSV
- **Efficacité offensive** : `buts_marqués / tirs_cadres`
- **Distribution temporelle** : Buts par tranche de 5'
- **Performances individuelles** : Buts/tirs par joueur
- **Défense** : Buts concédés / tirs concédés

### Exemple d'analyse
```markdown
## Analyse du match USAO U8 vs R.St.FC.Bouillon

**Score final** : 12-4 (VICTOIRE)

**Offensive** :
- 12 buts en 6 tirs = efficacité 200% (1 but/tir en moyenne)
- Nestor Arnould : 7 buts
- Maxence Jonckheere : 4 buts
- Lilou Douny : 1 but
- Auguste Robinet : 1 but

**Défense** :
- 4 buts concédés en 3 tirs de l'adversaire
- 2 Arrêts (frappe_créée inférée) : à min 34 et 42
```

## 9. Troubleshooting

| Problème | Cause | Solution |
|----------|-------|----------|
| CSV vide ou incorrect | Événements mal classés | Vérifier `side: left/right` dans JSON |
| Stats inversées (12-4 deviennent 4-12) | Logique de rapport inversée | Vérifier `classify_and_enrich_events()` |
| Joueurs non lisibles | Capture peu claire | Utiliser `"player": "adversaire"` |
| Minutes non cohérentes | Mal extraites de la capture | Relecturer l'heure sur la timeline |

## 10. Évolutions futures

- [ ] Implémentation d'OCR pour auto-extraction des textes des captures
- [ ] Support multi-langue (FR/EN/etc.)
- [ ] Graphiques de distribution temporelle
- [ ] Comparaison multi-matchs (tendances sur une saison)
- [ ] Export en formats supplémentaires (Excel, JSON, API)

---

**Dernière mise à jour** : 2025-11-07
**Outil de référence** : `/workspaces/mystuff/tools/parse_timeline.py`