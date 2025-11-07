# ⚡ Démarrage rapide (5 minutes)

## Objectif
Analyser les événements d'une timeline SportEasy et les classifier automatiquement par équipe.

## ✅ Ce que vous obtenez

1. **CSV** `parsed_by_side.csv` — Tous les événements classifiés
2. **Markdown** `.md` — Rapport formaté avec statistiques
3. **Inférences** — Frappes implicites détectées automatiquement

## 🚀 3 façons d'utiliser

### Option 1 : Fichier JSON (⭐ Recommandé)

**Étape 1 :** Créer `timeline.json`
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

**Étape 2 :** Exécuter
```bash
python tools/parse_timeline.py --input timeline.json --out-dir output
```

**Étape 3 :** Vérifier `output/parsed_by_side.csv`

---

### Option 2 : Mode interactif

**Étape 1 :** Lancer le script
```bash
python tools/parse_timeline.py --interactive
```

**Étape 2 :** Suivre les prompts
```
Enter match header: Paris 3-2 Lyon 2024/2025
  (Appuyer sur Entrée après chaque ligne)

Enter events one by one:
Minute: 45
Event type: But
Player: Mbappé
Side: left

Minute: 30
Event type: Arrêt
Player: Areola
Side: left

Minute: (vide pour terminer)
```

**Étape 3 :** Fichiers générés automatiquement

---

### Option 3 : Commande avancée

```bash
python tools/parse_timeline.py \
  --input timeline.json \
  --out-dir output \
  --matchday "2025-11-01" \
  --our-team "Paris"
```

---

## 📋 Format JSON minimal

```json
{
  "match_header": "ÉquipeA score-score ÉquipeB",
  "events": [
    {
      "minute": 45,
      "type": "Type d'événement",
      "player": "Nom du joueur (ou null)",
      "side": "left ou right"
    }
  ]
}
```

### Types d'événements reconnus
```
But, Carton Jaune, Carton Rouge, Remplacement,
Arrêt, Tir à côté, Poteau, Transversale, Tir arrêté, Blessé
```

### Side (côté)
- `"left"` = votre équipe (team1)
- `"right"` = adversaire (team2)

---

## 📊 Exemple complet (2 minutes)

### 1. JSON input
```json
{
  "match_header": "Paris 3-2 Lyon 2024/2025",
  "events": [
    {"minute": 90, "type": "But", "player": "Benzema", "side": "right"},
    {"minute": 85, "type": "Arrêt", "player": "Areola", "side": "left"},
    {"minute": 80, "type": "But", "player": "Messi", "side": "left"},
    {"minute": 60, "type": "Tir arrêté", "player": "Keeper Lyon", "side": "right"}
  ]
}
```

### 2. Commande
```bash
python tools/parse_timeline.py --input timeline.json --out-dir out
```

### 3. Résultats

**CSV** (`out/parsed_by_side.csv`) :
```
minute,type,player,side,team,classification,inferred_actions,confidence
90,But,Benzema,right,opponent,goal,,1.00
85,Arrêt,Areola,left,us,shoot,frappe_subite,1.00
80,But,Messi,left,us,goal,,1.00
60,Tir arrêté,Keeper Lyon,right,opponent,shoot,frappe_créée,1.00
```

**Markdown** (`out/YYYY-MM-DD.md`) :
```markdown
# Match: Paris 3 - 2 Lyon

## Résumé
- **Paris**: 2 buts, 0 tirs (+ 1 arrêt)
- **Lyon**: 1 buts, 1 tir arrêté

## Tous les événements
- 90' — But — Benzema [OPPONENT] — goal
- 85' — Arrêt — Areola [US] — shoot (inféré: frappe_subite)
- 80' — But — Messi [US] — goal
- 60' — Tir arrêté — Keeper Lyon [OPPONENT] — shoot (inféré: frappe_créée)
```

---

## 🧠 Comprendre les inférences

### Qu'est-ce que "frappe_subite" ?
= **L'adversaire a tiré et nous avons défendu**

Exemple : Vous avez un "Arrêt" à la minute 30
→ Cela signifie que l'adversaire a tiré et vous l'avez arrêté

### Qu'est-ce que "frappe_créée" ?
= **Nous avons tiré et l'adversaire a défendu**

Exemple : L'adversaire a un "Tir arrêté" à la minute 45
→ Cela signifie que vous avez tiré et l'adversaire l'a arrêté

**Pourquoi c'est utile ?** Parce que la timeline ne rapporte pas toujours explicitement tous les tirs!

---

## ⚠️ Points à retenir

✅ **Header :** Format `"Équipe1 score-score Équipe2"`

✅ **Side :** "left" = votre équipe (Équipe1), "right" = adversaire (Équipe2)

✅ **Types reconnus :** Il y a 10 types, vérifiez l'orthographe

✅ **Player :** Peut être null pour les événements sans joueur

✅ **Minute :** Entre 1 et 90

---

## 🎯 Cas d'usage

| Cas | Utiliser |
|-----|----------|
| Lire 1-2 images | Mode interactif |
| Lire plusieurs images | Fichier JSON + script |
| Analyser en Excel | Exporter CSV |
| Rapport lisible | Exporter Markdown |
| Intégration pipeline | Script + API |

---

## 📚 Documentation complète

- `README_OCR.md` — Vue d'ensemble
- `GUIDE_PARSE_TIMELINE.md` — Guide détaillé
- `EXAMPLES_TIMELINE.md` — Cas d'usage
- `SOLUTION_SUMMARY.md` — Architecture

---

## 💡 Conseils

1. **Commencez simple** → Faites un test avec 2-3 événements
2. **Vérifiez le header** → C'est critique pour la détection des équipes
3. **Vérifiez les types** → Doivent être dans la liste reconnue
4. **Utilisez "left"/"right"** → Pas "gauche"/"droite"
5. **Pour l'aide** → Utilisez `python tools/parse_timeline.py --help`

---

## ❓ Questions fréquentes

**Q: Dois-je vraiment lire les images manuellement?**
R: Oui, il n'y a pas d'OCR. Cela rend les résultats plus fiables.

**Q: Comment je sais quel côté est gauche/droite?**
R: Regardez l'ordre du header : première équipe = left, seconde = right

**Q: Que faire si un type d'événement n'est pas reconnu?**
R: Le parser l'ignore. Les types reconnus sont : But, Carton Jaune, Carton Rouge, Remplacement, Arrêt, Tir à côté, Poteau, Transversale, Tir arrêté, Blessé

**Q: Le fichier JSON peut être mal formé?**
R: Utilisez `python -m json.tool timeline.json` pour vérifier

---

## 🎓 Vous êtes prêt!

Maintenant :
1. Lisez vos captures timeline
2. Créez un JSON
3. Lancez le script
4. Analysez les résultats

Bonne chance! 🏆
