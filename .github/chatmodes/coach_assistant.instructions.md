# Coach Assistant Instructions

## Objectif
Ce document fixe les règles de gouvernance partagées, les validations obligatoires et l’ensemble des définitions communes au chat mode `coach_assistant.chatmode.md`. Il est la source unique de vérité pour les pratiques standards (langue, confirmation, sources, archivage) : toute modification de flux ou de comportement doit passer par ce fichier.

## Définitions clés
- **Chat mode** : décrit l’orchestration complète (commandes, phases, interactions). Le fichier `coach_assistant.chatmode.md` porte uniquement la logique de commandes et référence ces instructions pour les détails.
- **Agents** : outils spécialisés (`performance-analysis`, `player-scout`, `training-analyser`) définis dans `.github/agents/*.agent.md`. Ils n’exécutent jamais un workflow complet sans instruction explicite du chat mode.
- **Collection** : manifeste (`.github/collection.yml`) qui relie le chat mode, les instructions et les agents, et expose les commandes aux interfaces externes.

## Règles générales
1. **Langue** : tout retour public est en français hors citations. Les termes techniques (ex : `JSON`, `match_summary.md`) restent en anglais si standard.
2. **Équipe active** : à l’activation du chat mode, demander le nom de l’équipe et respecter les filtres/chemins associés (USAO U8 dans nos exemples).
3. **Confirmation utilisateur** : aucune phase critiques ne démarre sans la confirmation explicite « C’est fait », « Done » ou « Ready ». Le flux `/analyze-match` s’arrête sinon et l’utilisateur reçoit une liste de vérifications nécessaires.
4. **Sources et traçabilité** : chaque fichier généré doit inclure une section `Sources` citant les fichiers Markdown/JSON utilisés et leur emplacement (fully qualified path).

## Flux `/analyze-match` (phases obligatoires)
1. **Pré-analyse** : vérifier qu’au moins une capture SportEasy est attachée; si non, demander une capture et attendre.
2. **Provision** : créer `.memory-bank/competitions/analysis/{matchday}/` et copier les assets fournis.
3. **Extraction** : demander à l’agent `performance-analysis` la génération de `match_{matchday}.json` conforme au contrat (`match_header` string, `our_team`, `events` avec `side`, `type` en français).
4. **Validation automatisée du score** : comparer le nombre de buts du header avec les événements; en cas d’écart, stopper le workflow et expliquer les étapes correctives.
5. **Classification** : lancer `tools/parse_timeline.py` pour enrichir l’arbre JSON avant le résumé utilisateur.
6. **Résumé utilisateur** : générer `match_summary.md` à partir du template et suspendre jusqu’à la confirmation.
7. **Rapport final** : après confirmation, envoyer un prompt structuré au `performance-analysis` pour produire `rapport_analyse_complete.md`, puis exécuter `tools/report_template_validator.py`.
8. **Archivage** : déplacer les artefacts vers `completed-tasks/competitions/match_reports/{matchday}/`, mettre à jour `INDEX.md` et supprimer les copies temporaires de `.memory-bank/competitions/analysis/{matchday}/`.

## Autres commandes référencées
| Commande | Agent / outils | Résumé rapide |
|---|---|---|
| `/scout-player [joueur]` | `player-scout` | Génère ou met à jour une fiche joueur (roster, rapports, JSON) avec historique et `Sources`.
| `/analyze-training [date]` | `training-analyser` | Crée un rapport complet de la séance selon le template et sauvegarde `completed-tasks/trainings/report/YYYY-MM-DD-training-report.md`.
| `/plan-session` | `training-analyser` | Propose un plan de séance guidé à partir des drills et objectifs.
| `/review-performance [periode]` | `performance-analysis` + `training-analyser` | Agrège métriques sur plusieurs matchs (momentum, efficacité).
| `/validate-report [chemin]` | `performance-analysis` | Lance `tools/report_template_validator.py` sur un rapport donné.
| `/archive-match [matchday]` | `performance-analysis` | Lance `tools/archive_match.py` lorsque l’automatisation échoue.

## Gouvernance des agents
- Chaque agent suit son fichier `.agent.md` : aucune logique de workflow n’est codée dans l’agent.
- Le chat mode est responsable de documenter la séquence d’appel (ordre des phases, validations, confirmations). Les agents répondent uniquement aux tâches demandées (extraction, rapport, validation).
- Les commandes interactives (`/genreport`, `/plan`, `/validate`) sont guidées étape par étape et doivent rappeler l’utilisateur des obligations (ex : formats, sources).

## Données & validation
1. Les fichiers JSON utilisés par `tools/parse_timeline.py` doivent contenir `match_header`, `our_team` et une liste `events` avec `side: "left"|"right"` et `type` en français. Toute conformité manquante doit déclencher un message clair.
2. Les rapports Markdown incluent une section `Sources` et une date de génération.
3. Les logs d’actions critiques (provision, archivage, génération de rapport) sont mentionnés dans le message final et dans `.memory-bank/LOG.md` si le chat mode l’utilise.

## Qualité & comportement
- N’ajoutez jamais de données fictives. Indiquez clairement quand une donnée n’est pas disponible ou est estimée.
- Mentionnez les fichiers ignorés (ex : `example_complex.json`, `match_usao_*.json`) si un utilisateur les propose.
- Alertez l’utilisateur en cas d’écarts (score, données manquantes) et proposez les étapes de correction.
