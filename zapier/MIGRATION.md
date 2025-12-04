# Migration Guide: Chatmodes/Agents → Zapier Actions

Ce document explique comment l'ancien système basé sur chatmodes et agents a été migré vers une intégration Zapier.

## 📋 Vue d'ensemble

| Ancien Système | Nouveau Système Zapier |
|----------------|------------------------|
| `.github/chatmodes/` | `zapier/actions/` |
| `.github/agents/` | `zapier/actions/` + `zapier/schemas/` |
| Scripts interactifs | Scripts autonomes avec I/O JSON |
| Commandes manuelles | Webhooks automatisés |

## 🔄 Mapping des Commandes

### 1. `/analyze-match [matchday]`

**Avant:**
- Fichier: `.github/chatmodes/coach_assistant.chatmode.md`
- Agent: `.github/agents/performance-analysis.agent.md`
- Interaction: Manuelle avec confirmations

**Après:**
- Action: `zapier/actions/analyze_match.py`
- Schémas: `zapier/schemas/match_input.json` + `match_output.json`
- Mode: Automatisé via webhook
- Callback: Notification Zapier à la fin

**Exemple de migration:**

```yaml
# Avant (chatmode)
/analyze-match 2025-10-16
→ Agent demande confirmation
→ Utilisateur confirme chaque étape
→ Génération du rapport

# Après (Zapier)
POST /actions/analyze-match
{
  "matchday": "2025-10-16",
  "team_name": "USAO U8",
  "sources": {"screenshots": [...]},
  "options": {"auto_archive": true},
  "callback_url": "https://hooks.zapier.com/..."
}
→ Pipeline complet automatique
→ Callback avec résultats JSON
```

### 2. `/scout-player [joueur]`

**Avant:**
- Fichier: `.github/chatmodes/coach_assistant.chatmode.md`
- Agent: `.github/agents/player-scout.agent.md`
- Sources: Manuellement spécifiées

**Après:**
- Action: `zapier/actions/scout_player.py`
- Schémas: `zapier/schemas/player_input.json` + `player_output.json`
- Sources: Automatiquement collectées depuis Zapier

**Exemple de migration:**

```yaml
# Avant
/scout-player "Jean Dupont"
→ Agent recherche dans roster, trainings, competitions
→ Questions interactives
→ Mise à jour fiche

# Après (Zapier)
POST /actions/scout-player
{
  "player_name": "Jean Dupont",
  "sources": {
    "roster_files": [...],
    "training_reports": [...],
    "competition_reports": [...]
  },
  "update_mode": "merge"
}
→ Analyse automatique
→ Profil JSON + Markdown généré
```

### 3. `/analyze-training [date]`

**Avant:**
- Fichier: `.github/chatmodes/coach_assistant.chatmode.md`
- Agent: `.github/agents/training-analyser.agent.md`
- Interaction: Guidée, questions-réponses

**Après:**
- Action: `zapier/actions/analyze_training.py`
- Schémas: `zapier/schemas/training_input.json` + `training_output.json`
- Données: Précollectées (formulaire, Google Sheets, etc.)

**Exemple de migration:**

```yaml
# Avant
/analyze-training 2025-10-20
→ Questions sur drills, présences, notes
→ Génération interactive du rapport

# Après (Zapier)
POST /actions/analyze-training
{
  "date": "2025-10-20",
  "team_name": "USAO U8",
  "drills": [
    {"name": "...", "duration": 20, ...}
  ],
  "attendance": [...],
  "notes": "..."
}
→ Rapport généré automatiquement
```

## 🏗️ Architecture

### Ancien Système

```
Utilisateur
    ↓ (commande manuelle)
Chatmode (orchestrateur)
    ↓ (délègue)
Agent (exécuteur)
    ↓ (appelle)
Tools/Scripts Python
    ↓ (génère)
Artefacts (JSON, MD)
```

### Nouveau Système Zapier

```
Trigger (événement externe)
    ↓ (webhook)
Zapier
    ↓ (POST HTTP)
Action Python (zapier/actions/)
    ↓ (appelle)
Tools/Scripts Python (inchangés)
    ↓ (génère)
Artefacts (JSON, MD)
    ↓ (callback)
Zapier (notification/suite du Zap)
```

## 📊 Comparaison des Workflows

### Workflow 1: Analyse de Match

#### Ancien (Chatmode)
```
1. Utilisateur: "/analyze-match 2025-10-16"
2. Chatmode: "Confirmer que sources sont attachées? [Y/N]"
3. Utilisateur: "Y"
4. Agent performance-analysis: Extraction JSON
5. Chatmode: "Lancer classification? [Y/N]"
6. Utilisateur: "Y"
7. Agent: Exécute parse_timeline.py
8. Chatmode: "Générer rapport complet? [Y/N]"
9. Utilisateur: "Y"
10. Agent: Génère rapport
11. Chatmode: "Archiver? [Y/N]"
12. Utilisateur: "Y"
13. Agent: Archive avec archive_match.py
```

#### Nouveau (Zapier)
```
1. Trigger: Nouveau match dans Google Sheets/Form
2. Zapier: Collecte données (date, équipe, screenshots)
3. Zapier: POST /actions/analyze-match
4. Action: Pipeline complet automatique
   - Provision
   - Extraction
   - Classification (parse_timeline.py)
   - Build summary
   - Validation
   - Rapport complet
   - Archive (si option activée)
5. Action: Callback vers Zapier avec résultats
6. Zapier: Suite du Zap (email, Slack, etc.)
```

### Workflow 2: Scout Joueur

#### Ancien (Chatmode)
```
1. Utilisateur: "/scout-player Jean Dupont"
2. Agent: Cherche dans completed-tasks/roster
3. Agent: "Analyser trainings aussi? [Y/N]"
4. Utilisateur: "Y"
5. Agent: Parcourt trainings/report
6. Agent: "Analyser compétitions? [Y/N]"
7. Utilisateur: "Y"
8. Agent: Parcourt competitions
9. Agent: Génère fiche
```

#### Nouveau (Zapier)
```
1. Trigger: Joueur sélectionné dans interface
2. Zapier: Collecte ID joueur
3. Zapier: POST /actions/scout-player avec sources
4. Action: Analyse toutes sources automatiquement
5. Action: Génère profil JSON + MD
6. Action: Callback avec résultats
7. Zapier: Envoie notification au coach
```

## 🔧 Adaptations Techniques

### 1. Gestion des Confirmations

**Avant:** Requises à chaque étape critique
**Après:** Configurables via `options`

```json
{
  "options": {
    "auto_archive": false,        // Archivage manuel
    "generate_full_report": true, // Toujours générer
    "validate_template": true     // Toujours valider
  }
}
```

### 2. Sources de Données

**Avant:** Attachements manuels, questions interactives
**Après:** URLs, chemins de fichiers dans le JSON d'entrée

```json
{
  "sources": {
    "screenshots": [
      "https://drive.google.com/file/d/xyz",
      "https://dropbox.com/file/abc"
    ],
    "json_file": "https://..."
  }
}
```

### 3. Notifications

**Avant:** Messages textuels dans le chat
**Après:** Callbacks HTTP vers webhooks Zapier

```python
if self.callback_url:
    requests.post(self.callback_url, json=self.results)
```

### 4. Gestion d'Erreurs

**Avant:** Affichage dans le chat, retry manuel
**Après:** Codes d'erreur structurés, retry Zapier

```json
{
  "status": "error",
  "error": {
    "code": "ANALYSIS_ERROR",
    "message": "Score mismatch: header shows 12-5 but events total 11-5",
    "details": {
      "expected": {"home": 12, "away": 5},
      "actual": {"home": 11, "away": 5}
    }
  }
}
```

## 📁 Préservation des Agents

Les fichiers agents dans `.github/agents/` sont **préservés** car ils contiennent:
- La documentation des règles métier
- Les contrats d'interface (formats JSON)
- Les validations requises
- Les exemples et cas d'usage

**Ils servent maintenant de:**
1. Documentation de référence
2. Spécifications pour les actions Zapier
3. Guide pour les validations

## 🔄 Utilisation Hybride

Vous pouvez utiliser les deux systèmes en parallèle:

### Mode Interactif (Chatmode)
- Nouveaux matchs avec données incomplètes
- Exploration et debugging
- Formation et apprentissage

### Mode Automatisé (Zapier)
- Matchs réguliers avec processus établi
- Intégration avec autres outils (calendrier, CRM, etc.)
- Rapports automatiques hebdomadaires/mensuels

## 🚀 Exemples de Zaps

### Zap 1: Match Analysis Pipeline
```
Trigger: Nouveau match dans Google Sheets
↓
Filter: Match status = "Completed"
↓
Delay: Attendre 1 heure (téléchargement screenshots)
↓
Webhooks by Zapier: POST /actions/analyze-match
↓
Filter: status = "success"
↓
Gmail: Envoyer rapport au coach
↓
Slack: Notification équipe
```

### Zap 2: Weekly Player Review
```
Schedule: Tous les lundis 9h
↓
Google Sheets: Récupérer liste joueurs
↓
Loop: Pour chaque joueur
  ↓
  Webhooks: POST /actions/scout-player
  ↓
  Delay: 30 secondes
↓
Google Drive: Créer dossier avec tous les profils
↓
Email: Envoyer synthèse au staff
```

### Zap 3: Training Report
```
Trigger: Soumission Google Form (rapport d'entraînement)
↓
Formatter: Convertir données en JSON
↓
Webhooks: POST /actions/analyze-training
↓
Google Drive: Sauvegarder rapport MD
↓
Notion: Créer page avec résumé
```

## ✅ Checklist de Migration

- [x] Créer structure `zapier/`
- [x] Définir schémas JSON (input/output)
- [x] Implémenter actions Python
- [x] Documentation README
- [ ] Créer serveur Flask/FastAPI
- [ ] Déployer serveur (Heroku, Railway, AWS, etc.)
- [ ] Configurer Zaps dans Zapier
- [ ] Tests end-to-end
- [ ] Formation utilisateurs
- [ ] Migration progressive des workflows

## 🎯 Prochaines Étapes

1. **Implémenter le serveur web** (voir `zapier/README.md`)
2. **Tester chaque action** avec des données réelles
3. **Créer les premiers Zaps** pour les cas d'usage prioritaires
4. **Monitorer et optimiser** les performances
5. **Étendre** avec de nouvelles actions (plan-session, review-performance, etc.)

## 📚 Références

- Configuration Zapier: `zapier/config/zapier.config.json`
- Schémas: `zapier/schemas/`
- Actions: `zapier/actions/`
- Documentation: `zapier/README.md`
- Ancien système: `.github/chatmodes/` et `.github/agents/`
