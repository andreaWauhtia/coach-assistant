# Prompt: /analyze-match [matchday]

Ce prompt définit le pipeline complet d'analyse de match pour l'agent `performance-analysis` sous la direction du `coach_assistant`.

## Phases obligatoires

1. **Pré-analyse** : 
   - Vérifier qu'au moins une capture d'écran SportEasy est attachée ou disponible.
   - Confirmer le nom de l'équipe (ex : USAO U8).

2. **Provisioning** : 
   - Créer le dossier de travail : `.memory-bank/competitions/analysis/{matchday}/`.
   - Copier les sources (images, JSON bruts) dans ce dossier.

3. **Extraction (Vision)** : 
   - Appeler l'agent `performance-analysis` (ou utiliser ses capacités d'extraction).
   - Utiliser strictement `.github/prompts/match_extraction.prompt.md`.
   - Générer `match_{matchday}.json`.

4. **Validation du Score** : 
   - Comparer le score du header (ex: "12-5") avec le décompte des événements "But" dans le JSON.
   - **Règle critique** : Si mismatch, stopper immédiatement et demander clarification.

5. **Classification & Enrichissement** : 
   - Exécuter `tools/parse_timeline.py` sur le JSON extrait.
   - Produire le JSON enrichi.

6. **Résumé (Draft)** : 
   - Générer `match_summary.md` dans le dossier d'analyse.
   - Attendre la confirmation utilisateur ("Ready" / "C'est fait").

7. **Rapport Final** : 
   - Générer `rapport_analyse_complete.md` en utilisant le template `templates/rapport_analyse_complete.md`.
   - Valider le rapport avec `tools/report_template_validator.py`.

8. **Archivage** : 
   - Déplacer tous les artefacts finaux vers `completed-tasks/competitions/match_reports/{matchday}/`.
   - Nettoyer le dossier temporaire dans `.memory-bank`.

## Contraintes
- Toujours inclure une section `Sources` listant les fichiers exacts utilisés.
- Requérir une confirmation explicite avant les étapes critiques (Extraction, Rapport Final, Archivage).
- En cas d'erreur technique ou de données manquantes, arrêter le pipeline et proposer une solution.
