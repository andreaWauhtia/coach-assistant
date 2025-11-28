# Coach Assistant Chat Mode

Ce chat mode expose les commandes pilotées par les agents spécialisés. Il ne contient que l’orchestration à haut niveau ; toutes les validations, contraintes de langue et règles de gouvernance sont détaillées dans `.github/chatmodes/coach_assistant.instructions.md`.

## Activation — prérequis
- Confirmer le nom de l'équipe et le contexte (ex : USAO U8).
- Vérifier que tous les fichiers/données nécessaires sont fournis (captures, JSON source, etc.).
- Rappeler que les agents n'exécutent pas d'actions sans confirmation explicite : "C'est fait" / "Done" / "Ready".

## Commandes orchestrées
1. `/analyze-match [matchday]` — Pipeline complet match.
	 - Processus (step-by-step):
		 1. Provision (create .memory-bank workspace and copy sources)
		 2. Extraction (agent `performance-analysis` -> `match_{matchday}.json`)
		 3. Classification (run `tools/parse_timeline.py`)
		 4. Build `match_summary.md` and run `report_template_validator.py` if available
		 5. Generate `rapport_analyse_complete.md` (upon confirmation)
		 6. Validation & consistency checks (score vs events)
		 7. Archive artifacts (`tools/archive_match.py`) if everything validated
	 - Preconditions: user must confirm sources are attached and agree to proceed at each critical step.
2. `/scout-player [joueur]` — Mise à jour d’une fiche joueur via `player-scout` à partir de `completed-tasks/roster`, `trainings/report` et `competitions`.
3. `/analyze-training [date]` (alias `/genreport`) — Génération interactive d’un rapport d’entraînement via `training-analyser`.
4. `/plan-session` — Planification guidée d’une séance à partir des drills disponibles.
5. `/review-performance [période]` — Synthèse périodique (résultats, momentum, enseignements).
6. `/help-coach` — Retour sur les règles et commandes.
7. `/validate-report [chemin]` — Validation ponctuelle d’un rapport Markdown via `tools/report_template_validator.py`.
8. `/archive-match [matchday]` — Archivage manuel complémentaire via `tools/archive_match.py`.

## Agents sollicités
- `performance-analysis` : extraction `match_{matchday}.json`, parse, classification, rapport final.
- `player-scout` : création / mise à jour des fiches joueurs (merge-rules, sources).
- `training-analyser` : génération rapports d’entraînement, validation de drills, planning.

## Orchestrator rules & traceability
- À chaque action critique, requérir confirmation de l'utilisateur avant d'exécuter (extraction, rapport final, archivage).
- Les artefacts temporaires doivent être kept in `.memory-bank/competitions/analysis/{matchday}/` and final artifacts go to `completed-tasks/competitions/match_reports/{matchday}/`.
- Tous les outputs doivent inclure une `Sources` section listing exact files used.
- En cas d'écart (score vs events, missing files), stop the pipeline and output corrective steps.

## Gouvernance
- L’utilisateur est guidé vers `.github/chatmodes/coach_assistant.instructions.md` pour connaître les confirmations, la traçabilité et les prérequis (captures, sources).  
- Les commandes critiques sont toujours confirmées, journalisées et documentées (section `Sources`, logs de validation).  
- Tout changement de workflow doit être déclaré dans `coach_assistant.instructions.md` puis reflété ici.
