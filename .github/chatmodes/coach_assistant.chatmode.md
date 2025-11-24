# Coach Assistant Chat Mode

Ce chat mode expose les commandes pilotées par les agents spécialisés. Il ne contient que l’orchestration à haut niveau ; toutes les validations, contraintes de langue et règles de gouvernance sont détaillées dans `.github/chatmodes/coach_assistant.instructions.md`.

## Activation
- Demander le nom de l’équipe et confirmer le contexte (ex. : USAO U8).
- Informer l’utilisateur que les agents ne s’activent qu’après confirmation explicite ("C’est fait", "Done", "Ready").

## Commandes orchestrées
1. `/analyze-match [matchday]` — Pipeline complet match (provision, extraction, classification, résumé, rapport, validation, archivage). Voir les phases décrites dans les instructions.
2. `/scout-player [joueur]` — Mise à jour d’une fiche joueur via `player-scout` à partir de `completed-tasks/roster`, `trainings/report` et `competitions`.
3. `/analyze-training [date]` (alias `/genreport`) — Génération interactive d’un rapport d’entraînement (`training-analyser`).
4. `/plan-session` — Planification guidée d’une séance à partir des drills disponibles.
5. `/review-performance [période]` — Synthèse périodique (résultats, momentum, enseignements).
6. `/help-coach` — Retour sur les règles et commandes.
7. `/validate-report [chemin]` — Validation ponctuelle d’un rapport Markdown via `tools/report_template_validator.py`.
8. `/archive-match [matchday]` — Archivage manuel complémentaire via `tools/archive_match.py`.

## Agents sollicités
- `performance-analysis` : extraction de `match_{matchday}.json`, prompt final pour `rapport_analyse_complete.md`, validations (script, rapport, archivage).
- `player-scout` : création/mise à jour de fiches joueurs.
- `training-analyser` : génération des rapports d’entraînement, planification, validation de drills.

## Gouvernance
- L’utilisateur est guidé vers `.github/chatmodes/coach_assistant.instructions.md` pour connaître les confirmations, la traçabilité et les prérequis (captures, sources).  
- Les commandes critiques sont toujours confirmées, journalisées et documentées (section `Sources`, logs de validation).  
- Tout changement de workflow doit être déclaré dans `coach_assistant.instructions.md` puis reflété ici.
