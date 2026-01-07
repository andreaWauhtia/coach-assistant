# Prompt: /analyze-training [date] (alias /genreport)

Ce prompt définit le processus interactif de génération de rapport d'entraînement pour l'agent `training-analyser`.

## Objectif
Générer un rapport structuré (`YYYY-MM-DD-training-report.md`) dans `completed-tasks/trainings/report/`.

## Processus Interactif (Questions)

1. **Informations Générales** :
   - Type de séance (corrective, technique, tactique, préparation).
   - Durée (minutes).
   - Présents (n/14).
   - Conditions (météo, terrain).

2. **Objectifs** :
   - Définir 1 à 3 objectifs (technique, tactique, comportemental).

3. **Exercices Réalisés** :
   - Pour chaque exercice : Nom, Source (`drills/`), Pertinence (1-5), Efficacité (1-5), Adaptations.

4. **Observations** :
   - Individuelles : 3 joueurs en progression + 3 points d'attention max.
   - Groupe : Ce qui a marché, points à améliorer, engagement.

5. **Bilan & Suite** :
   - Priorités pour la prochaine séance.
   - Recommandations d'exercices futurs.
   - Communication parents & KPI.

## Format du Rapport (Markdown)
- Structure stricte définie dans `training-analyser.agent.md`.
- Langue : Français.
- Section `Sources` obligatoire.

## Validations
- Date au format `YYYY-MM-DD`.
- Présence des champs obligatoires.
- Calcul automatique des notes par domaine (Technique, Collectif, Attitude).
