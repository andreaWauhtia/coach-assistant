# Prompt: /analyze-match-custom [matchday]

Ce prompt définit le pipeline d'analyse de match pour l'agent `performance-analysis` utilisant les données d'app personnalisée (JSON profils joueurs + Markdown événements match).

## Phases obligatoires

1. **Pré-analyse** :
   - Vérifier que les données sont fournies : profils joueurs JSON et/ou événements match Markdown.
   - Confirmer le nom de l'équipe et la date du match.

2. **Provisioning** :
   - Créer le dossier de travail : `.memory-bank/competitions/analysis/{matchday}/`.
   - Copier/sauvegarder les sources (JSON profils, Markdown événements) dans ce dossier.

3. **Extraction (Parsing)** :
   - Pour les événements Markdown : exécuter `tools/parse_markdown_table.py` pour convertir en JSON structuré.
   - Pour les profils JSON : valider la structure et intégrer les données de base.
   - Générer `match_{matchday}.json` consolidé.

4. **Validation du Score** :
   - Comparer le score indiqué dans les données avec le décompte des événements "Goal" dans le JSON.
   - **Règle critique** : Si mismatch, stopper immédiatement et demander clarification.

5. **Classification & Enrichissement** :
   - Si nécessaire, enrichir le JSON avec des classifications supplémentaires.
   - Intégrer les données de profils joueurs pour le contexte.

6. **Résumé (Draft)** :
   - Générer `match_summary.md` dans le dossier d'analyse basé sur les données parsées.
   - Attendre la confirmation utilisateur ("Ready" / "C'est fait").

7. **Rapport Final** :
   - Exécuter `tools/simulate_performance_analysis.py` pour générer automatiquement `rapport_analyse_complete.md`.
   - Le script utilise le template `templates/rapport_analyse_complete.md` et produit un rapport complet avec métriques équipe, stats individuelles, réseaux de passes, analyse temporelle et momentum.

8. **Archivage** :
   - Déplacer tous les artefacts finaux vers `completed-tasks/competitions/match_reports/{matchday}/`.
   - Nettoyer le dossier temporaire dans `.memory-bank`.

## Contraintes
- Toujours inclure une section `Sources` listant les fichiers JSON/Markdown utilisés.
- Requérir une confirmation explicite avant les étapes critiques (Extraction, Rapport Final, Archivage).
- En cas d'erreur technique ou de données manquantes, arrêter le pipeline et proposer une solution.
- Prioriser les données structurées (JSON/Markdown parsé) sur les données non structurées.</content>
<parameter name="filePath">d:\Dev\Dave\coach-assistant-main\.github\prompts\analyze_match_custom.prompt.md