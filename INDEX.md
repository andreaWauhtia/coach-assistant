# 📚 Index de la documentation

## 🚀 Commencer maintenant

1. **[⚡ QUICKSTART.md](./QUICKSTART.md)** — Démarrage en 5 minutes
   - 3 façons d'utiliser
   - Exemple complet
   - Questions fréquentes

## 📖 Documentation principale

2. **[📋 README_OCR.md](./README_OCR.md)** — Vue d'ensemble du projet
   - Workflow
   - Format JSON
   - Exemples de sortie

3. **[📚 GUIDE_PARSE_TIMELINE.md](./GUIDE_PARSE_TIMELINE.md)** — Guide complet
   - Format d'entrée détaillé
   - Types d'événements
   - Modes d'utilisation
   - Résultat CSV expliqué

4. **[💡 EXAMPLES_TIMELINE.md](./EXAMPLES_TIMELINE.md)** — Cas d'usage en détail
   - 5 exemples progressifs
   - Interprétation complète
   - Mode interactif pas à pas

## ✨ Résumés et changements

5. **[🏆 SOLUTION_SUMMARY.md](./SOLUTION_SUMMARY.md)** — Résumé de la solution
   - Architecture
   - Features clés
   - Logique métier

6. **[📝 CHANGES.md](./CHANGES.md)** — Journal des changements
   - Refactorisation
   - Nouvelles fonctions
   - Tests effectués

---

## 🎯 Parcours par profil utilisateur

### Je suis pressé ⏱️
→ Lisez **[⚡ QUICKSTART.md](./QUICKSTART.md)** (5 min)
- Exemple complet
- Commandes prêtes à copier-coller

### Je veux comprendre le flux 🔄
→ Lisez **[📋 README_OCR.md](./README_OCR.md)** (10 min)
- Workflow complet
- Format JSON
- Résultats attendus

### Je veux tous les détails 🔍
→ Lisez **[📚 GUIDE_PARSE_TIMELINE.md](./GUIDE_PARSE_TIMELINE.md)** (20 min)
- Format exact
- Tous les types d'événements
- Options avancées

### Je veux des exemples concrets 💡
→ Lisez **[💡 EXAMPLES_TIMELINE.md](./EXAMPLES_TIMELINE.md)** (15 min)
- 5 cas d'usage réels
- Interprétation complète
- Mode interactif

### Je veux connaître l'architecture 🏗️
→ Lisez **[🏆 SOLUTION_SUMMARY.md](./SOLUTION_SUMMARY.md)** (10 min)
- Logique métier
- Features principales
- Points forts

---

## 📁 Fichiers du projet

### Scripts
```
tools/
  └─ parse_timeline.py      ⭐ Script principal (refactorisé)
```

### Documentation
```
README_OCR.md               📋 Overview
README.md                   📖 Racine
QUICKSTART.md               ⚡ Démarrage rapide
GUIDE_PARSE_TIMELINE.md     📚 Guide complet
EXAMPLES_TIMELINE.md        💡 Exemples détaillés
SOLUTION_SUMMARY.md         🏆 Résumé de solution
CHANGES.md                  📝 Changements
INDEX.md                    📚 Ce fichier
```

### Exemples
```
example_timeline.json       🎯 Exemple simple (6 événements)
example_complex.json        🎯 Exemple complexe (10 événements)
```

### Résultats (exemples)
```
output/                     📊 Test simple
output_complex/             📊 Test complexe
output_interactive/         📊 Mode interactif
```

---

## 🔑 Concepts clés

### Match Header
```
Format: "Équipe1 score1-score2 Équipe2 [saison]"
Exemple: "Paris 3-2 Lyon 2024/2025"

Équipe1 (à gauche)   = NOTRE ÉQUIPE ("us")
Équipe2 (à droite)   = ADVERSAIRE ("opponent")
```

### Types d'événements
```
But                  → Classification: goal
Tir à côté/Poteau    → Classification: shoot
Arrêt/Tir arrêté     → Classification: shoot + inférence
Carton Jaune/Rouge   → Classification: card
Remplacement         → Classification: substitution
Blessé               → Classification: injury
```

### Inférences intelligentes
```
Si NOUS avons "Arrêt"           → frappe_subite
(l'adversaire a tiré sur nous)

Si ADVERSAIRE a "Arrêt"         → frappe_créée
(nous avons tiré sur l'adversaire)
```

---

## 💻 Utilisation rapide

### Option 1 : Fichier JSON
```bash
python tools/parse_timeline.py --input data.json --out-dir output
```

### Option 2 : Mode interactif
```bash
python tools/parse_timeline.py --interactive
```

### Option 3 : Avancé
```bash
python tools/parse_timeline.py \
  --input data.json \
  --out-dir output \
  --matchday "2025-11-01"
```

---

## 📊 Sorties générées

### parsed_by_side.csv
Tableau complet avec :
- minute, type, player
- side (left/right)
- team (us/opponent)
- classification (goal/shoot/card/...)
- inferred_actions (frappe_subite/créée)
- confidence (0.0-1.0)

### {matchday}.md
Rapport Markdown avec :
- Titre du match
- Résumé (buts, tirs par équipe)
- Distribution temporelle
- Liste complète des événements

---

## ✅ Check-list avant de commencer

- [ ] Vous avez les captures timeline SportEasy
- [ ] Vous avez Python 3.6+
- [ ] Vous avez lu [⚡ QUICKSTART.md](./QUICKSTART.md)
- [ ] Vous avez créé un fichier `timeline.json` OU vous prêt pour le mode interactif
- [ ] Vous comprenez le format du header
- [ ] Vous connaissez les types d'événements reconnus

---

## 🎓 Prochaines étapes

1. **Lire** [⚡ QUICKSTART.md](./QUICKSTART.md)
2. **Créer** un fichier JSON avec vos données
3. **Exécuter** `python tools/parse_timeline.py --input file.json`
4. **Vérifier** les fichiers `parsed_by_side.csv` et `.md`
5. **Analyser** vos données!

---

## 📞 Besoin d'aide?

- **Je veux juste commencer** → [⚡ QUICKSTART.md](./QUICKSTART.md)
- **Je ne comprends pas le format** → [📚 GUIDE_PARSE_TIMELINE.md](./GUIDE_PARSE_TIMELINE.md)
- **Je veux voir un exemple** → [💡 EXAMPLES_TIMELINE.md](./EXAMPLES_TIMELINE.md)
- **Je veux comprendre l'archi** → [🏆 SOLUTION_SUMMARY.md](./SOLUTION_SUMMARY.md)
- **Qu'est-ce qui a changé?** → [📝 CHANGES.md](./CHANGES.md)

---

## 🎉 Vous êtes prêt!

Commencez par **[⚡ QUICKSTART.md](./QUICKSTART.md)** et bon courage! 🏆
