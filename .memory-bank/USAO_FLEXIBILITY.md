# Flexibilité USAO U8: HOME vs AWAY

## Résumé

Le système de parsing de timelines SportEasy s'adapte **automatiquement** peu importe que USAO U8 soit :
- **HOME (left)** dans le header : `"USAO U8 15-2 Adversaire 2025/2026"`
- **AWAY (right)** dans le header : `"Adversaire 2-15 USAO U8 2025/2026"`

## Fonctionnement automatique

### Détection du côté

Lors de l'exécution avec `--our-team "USAO U8"`, le script :
1. Parse le header pour extraire team1 (LEFT/HOME) et team2 (RIGHT/AWAY)
2. Compare les noms avec `--our-team` (case-insensitive, trimmed)
3. Assigne `our_side = 'left'` si USAO = team1, ou `our_side = 'right'` si USAO = team2
4. Affiche : `👥 Our team: USAO U8 (HOME/left)` ou `👥 Our team: USAO U8 (AWAY/right)`

### Classification adaptative

La fonction `classify_and_enrich_events()` reçoit maintenant `our_team_side` et ajuste la logique :

```python
if our_team_side == 'left':
    # USAO U8 est HOME (left)
    side=left → team=us
    side=right → team=opponent
elif our_team_side == 'right':
    # USAO U8 est AWAY (right)
    side=right → team=us
    side=left → team=opponent
```

## Exemples

### Cas 1 : USAO U8 AWAY (right)
**Header** : `"R.St.FC.Bouillon 4-12 USAO U8 2025/2026"`
**Résultat** : `👥 Our team: USAO U8 (AWAY/right)`
```csv
minute,type,player,side,team,classification
4,But,Nestor Arnould,right,us,goal         ← USAO à droite = us
12,Tir à côté,adversaire,left,opponent,shoot   ← Adversaire à gauche = opponent
```

### Cas 2 : USAO U8 HOME (left)
**Header** : `"USAO U8 15-2 FC Test 2025/2026"`
**Résultat** : `👥 Our team: USAO U8 (HOME/left)`
```csv
minute,type,player,side,team,classification
3,But,Nestor Arnould,left,us,goal         ← USAO à gauche = us
8,But,adversaire,right,opponent,goal       ← Adversaire à droite = opponent
```

## Inférence (fonctionne dans les deux cas)

**Frappe_subite** (l'adversaire a tiré sur nous) :
- Cas AWAY : `team=us` + `Arrêt` (right) → frappe_subite ✅
- Cas HOME : `team=us` + `Arrêt` (left) → frappe_subite ✅

**Frappe_créée** (nous avons tiré) :
- Cas AWAY : `team=opponent` + `Arrêt` (left) → frappe_créée ✅
- Cas HOME : `team=opponent` + `Arrêt` (right) → frappe_créée ✅

## Commande standard

Quoiqu'il en soit le côté, la commande reste la même :
```bash
python tools/parse_timeline.py \
  --input match_YYYYMMDD.json \
  --out-dir analysis_output \
  --our-team "USAO U8"
```

Le script détecte automatiquement le côté et s'adapte! 🎯

---

**Dernière mise à jour** : 2025-11-07
**Script de référence** : `/workspaces/mystuff/tools/parse_timeline.py`
**Documentation** : `.memory-bank/timelineDataExtractions.md`
