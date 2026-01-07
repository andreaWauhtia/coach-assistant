# Prompt: Commandes Secondaires

Ce prompt regroupe les instructions pour les commandes utilitaires et de support.

## /list-players
- **Agent** : `player-scout`
- **Action** : Parcourir `completed-tasks/roster/*.md`.
- **Sortie** : Tableau Markdown (Prénom — Rôle — Fichier source).

## /listdrills
- **Agent** : `training-analyser`
- **Action** : Lister les fichiers dans `completed-tasks/trainings/drills/`.
- **Sortie** : Liste avec brèves descriptions.

## /validate [drill_name]
- **Agent** : `training-analyser`
- **Action** : Analyser un fichier drill (structure, adaptation catégorie d'âge).
- **Sortie** : Rapport de validation sauvegardé dans `completed-tasks/trainings/drills-validation/`.

## /validate-report [chemin]
- **Agent** : `coach_assistant` / `performance-analysis`
- **Action** : Exécuter `tools/report_template_validator.py`.
- **Sortie** : Statut de conformité.

## /archive-match [matchday]
- **Agent** : `coach_assistant` / `performance-analysis`
- **Action** : Exécuter `tools/archive_match.py`.
- **Sortie** : Confirmation du déplacement des fichiers.

## /review-performance [période]
- **Agent** : `coach_assistant`
- **Action** : Utiliser `tools/aggregate_matches.py` pour synthétiser les données sur une période.

## /help-coach / /help-scout
- **Action** : Afficher l'aide spécifique à l'agent et rappeler les règles de gouvernance.
