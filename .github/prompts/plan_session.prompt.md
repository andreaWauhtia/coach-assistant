# Prompt: /plan-session (alias /plan)

Ce prompt définit la planification guidée d'une séance d'entraînement pour l'agent `training-analyser`.

## Objectif
Générer un plan de séance personnalisé (`YYYY-MM-DD-training-plan.md`) dans `completed-tasks/trainings/plans/`.

## Étapes de Planification

1. **Base de Planification** :
   - Choisir entre : Objectifs à atteindre (proactif) OU Observations des derniers matchs (réactif).

2. **Affinage des Besoins** :
   - Priorités spécifiques (ex: conduite de balle, soutien).
   - Conditions (météo, effectif, matériel).
   - Niveau du groupe (adaptations U8).

3. **Recommandations Automatiques** :
   - Type de séance.
   - Sélection d'exercices depuis `completed-tasks/trainings/drills/`.
   - Structure temporelle (Échauffement, Technique, Opposition, Retour au calme).

4. **Sortie** :
   - Plan détaillé avec objectifs clairs et indicateurs de réussite.
   - Sauvegarde au format Markdown.

## Contraintes
- Utiliser uniquement les drills validés ou disponibles dans le dépôt.
- Respecter les contraintes d'âge (U8).
