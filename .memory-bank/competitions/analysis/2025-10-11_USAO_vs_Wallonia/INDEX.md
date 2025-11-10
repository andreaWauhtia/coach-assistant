# INDEX — Match USAO U8 25-0 Wallonia libin

**📅 Date** : 11 octobre 2025  
**🆚 Adversaire** : Wallonia libin  
**🎯 Compétition** : Match régulier U8 2025/2026  

---

## 📂 Fichiers d'Analyse

### 📊 Données Structurées

| Fichier | Description | Format | Utilisation |
|---------|-------------|--------|------------|
| **2025-10-11_USAO_vs_Wallonia.json** | Données parsées enrichies avec classifications complètes | JSON | Accès programmatique, intégrations |
| **parsed_by_side.csv** | Événements bruts (minute, type, joueur, équipe, classification, inférence) | CSV | Tableaux croisés dynamiques, filtres statistiques |
| **2025-10-11_USAO_vs_Wallonia.md** | Timeline chronologique (résumé + distribution + événements complets) | Markdown | Lecture visuelle rapide, rapports |

### 📈 Rapports d'Analyse

| Fichier | Description | Contenu | Audience |
|---------|-------------|---------|----------|
| **rapport_analyse_complete.md** | ⭐ **Rapport synthétique complet** | Métriques, performances individuelles, points forts, axes d'amélioration, recommandations | Entraîneurs, éducateurs, parents |

### 🔗 Fichier Source Original

| Fichier | Description |
|---------|-------------|
| `/workspaces/mystuff/match_20251011_USAO_Wallonia.json` | JSON source extrait des captures d'écran SportEasy |

---

## 📊 Résumé des Données

```
Match: USAO U8 25 - 0 Wallonia libin
Date: 11 octobre 2025
Durée: ~50 minutes (match complet)

USAO U8:
  - Buts marqués: 25
  - Tirs total: 30
  - Efficacité: 83.3%
  - Buteurs: 8 joueurs différents
  - Passes décisives: 5

Wallonia libin:
  - Buts marqués: 0
  - Tirs total: 9
  - Efficacité: 0%
  - Arrêts/Tirs arrêtés: 9
```

---

## 🎯 Metriques Clés

- **Efficacité offensive USAO** : 83.3% (25/30)
- **Efficacité défensive adverse** : 0% (0/9)
- **Ratio tirs** : 3.3:1 (USAO vs Wallonia)
- **Tempo moyen** : 2.5 buts/5 minutes
- **Constance** : Domination uniforme P1 et P2 (13 buts vs 12 buts)

---

## 👥 Top Performances

### 🏆 Buteurs (Top 5)

1. **Nestor Arnould** — 10 buts en 12 tirs (83.3%)
2. **Tiago Wauthia** — 5 buts en 5 tirs (100%)
3. **Maxence Jonckheere** — 5 buts en 6 tirs (83.3%) + 3 passes décisives
4. **Nathan Blyweert Doumont** — 2 buts en 2 tirs (100%)
5. **Lilou Douny** — 2 buts en 2 tirs (100%)

### 🎯 Passes Décisives

- Maxence Jonckheere : 3 passes
- Nestor Arnould : 1 passe
- Lilou Douny : 1 passe
- Robin Lambert : 1 passe

---

## 🔍 Points d'Accès Rapides

### Par Cas d'Usage

**Je veux...** → **Lire ce fichier**

- Comprendre le match rapidement → `rapport_analyse_complete.md` (section Résumé Exécutif)
- Voir tous les événements chronologiquement → `2025-10-11_USAO_vs_Wallonia.md`
- Analyser les tirs par tranche → `parsed_by_side.csv` + filtrer par `classification`
- Extraire les passes décisives → `2025-10-11_USAO_vs_Wallonia.json` (champ `note`)
- Vérifier l'efficacité par joueur → `rapport_analyse_complete.md` (Performances Individuelles)
- Obtenir des données pour Excel → `parsed_by_side.csv`
- Intégrer dans un système → `2025-10-11_USAO_vs_Wallonia.json`

---

## 📋 Procédure de Génération

**Étapes du pipeline** :
1. ✅ Extraction manuelle : captures d'écran SportEasy → JSON (`match_20251011_USAO_Wallonia.json`)
2. ✅ Parsing automatisé : `parse_timeline.py --our-team "USAO U8"`
3. ✅ Génération rapports : 3 fichiers structurés (JSON, CSV, MD)
4. ✅ Analyse synthétique : `rapport_analyse_complete.md`

**Commande** :
```bash
python tools/parse_timeline.py \
  --input match_20251011_USAO_Wallonia.json \
  --out-dir .memory-bank/competitions/analysis/2025-10-11_USAO_vs_Wallonia \
  --matchday "2025-10-11_USAO_vs_Wallonia" \
  --our-team "USAO U8"
```

---

## 📌 Validations

- ✅ **Total buts** : 25 (compté depuis CSV)
- ✅ **Total tirs USAO** : 30 (25 buts + 5 hors cadre)
- ✅ **Total tirs adversaires** : 9 (toutes inférences)
- ✅ **Événements parsés** : 43 (correspond aux captures d'écran)
- ✅ **Joueurs détectés** : 8 buteurs + adversaires
- ✅ **Passes décisives** : 5 inférées du texte SportEasy

---

## 🔗 Liens Contextuels

- **Dossier d'analyse** : `.memory-bank/competitions/analysis/2025-10-11_USAO_vs_Wallonia/`
- **Documentation pipeline** : `.memory-bank/timelineDataExtractions.md`
- **Flexibilité HOME/AWAY** : `.memory-bank/USAO_FLEXIBILITY.md`
- **Script source** : `/workspaces/mystuff/tools/parse_timeline.py`

---

**Généré le** : 7 novembre 2025  
**Version** : 1.0  
**Statut** : ✅ Analyse complète et validée
