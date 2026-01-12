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
3. **Confirmation utilisateur** : aucune phase critique ne démarre sans la confirmation explicite « C’est fait », « Done » ou « Ready ».
4. **Sources et traçabilité** : chaque fichier généré doit inclure une section `Sources` citant les fichiers Markdown/JSON utilisés et leur emplacement (fully qualified path).
5. **Qualité & comportement** : N’ajoutez jamais de données fictives. Indiquez clairement quand une donnée n’est pas disponible ou est estimée. Alertez l’utilisateur en cas d’écarts (score, données manquantes).

## Gouvernance des agents
- Chaque agent suit son fichier `.agent.md` : aucune logique de workflow n’est codée dans l’agent.
- Le chat mode est responsable de documenter la séquence d’appel (ordre des phases, validations, confirmations). Les agents répondent uniquement aux tâches demandées (extraction, rapport, validation).
- Les commandes interactives sont guidées étape par étape et doivent rappeler l’utilisateur des obligations (ex : formats, sources).

## Données & validation
1. Les fichiers JSON utilisés par `tools/parse_timeline.py` doivent respecter le contrat défini dans `.github/prompts/match_extraction.prompt.md`.
2. Les rapports Markdown incluent une section `Sources` et une date de génération.
3. Les logs d’actions critiques sont mentionnés dans le message final.
