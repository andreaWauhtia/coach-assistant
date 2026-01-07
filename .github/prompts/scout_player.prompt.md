# Prompt: /scout-player [joueur]

Ce prompt définit la méthodologie de scouting et de mise à jour des fiches joueurs pour l'agent `player-scout`.

## Objectif
Produire ou mettre à jour une fiche d'analyse factuelle (`[FirstName]_profile_analysis.md`) basée sur les données du dépôt.

## Étapes de traitement

1. **Identification du Joueur** :
   - Confirmer le nom complet.
   - Gérer les homonymes ou surnoms en proposant des choix.

2. **Collecte des Données (Sources)** :
   - **Roster** : `completed-tasks/roster/*.md`.
   - **Entraînements** : `completed-tasks/trainings/report/*.md` et `.memory-bank/trainings/report/*.md`.
   - **Compétitions** : `completed-tasks/competitions/match_reports/{matchday}/{matchday}.json` et `match_summary.md`.
   - **Note** : Exclure strictement les fichiers d'exemple (`example_*.json`, `match_usao_*.json`).

3. **Analyse & Agrégation** :
   - Chronologie des observations.
   - Statistiques (buts, passes, tirs, présences).
   - Tendances (progression, points d'attention).
   - **Règle** : Ne jamais inventer. Si absent, noter "Données non disponibles".

4. **Génération / Mise à jour (Merge)** :
   - Utiliser `templates/player_profile_template.md` si disponible.
   - **Règle de Fusion** : Ne jamais écraser les commentaires manuels. Ajouter les nouvelles données en conservant l'historique.
   - Langue : Français uniquement.

5. **Validation & Sauvegarde** :
   - Vérifier la présence de la section `Sources`.
   - Valider avec `tools/report_template_validator.py`.
   - Sauvegarder dans `completed-tasks/roster/{FirstName}_profile_analysis.md`.

## Commandes liées
- `/scout [player_name]` (alias)
- `/update-scout [player_name]` (incrémental)
- `/list-players` (tableau récapitulatif)
- `/fantasy-scout [player_name]` (projection spéculative)
