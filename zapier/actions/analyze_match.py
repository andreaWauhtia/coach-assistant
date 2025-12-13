#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Action Zapier: Analyze Match
Pipeline complet d'analyse de match compatible Zapier
"""
import json
import sys
import io
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

# Fix encodage UTF-8 pour Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import subprocess

# Ajouter le répertoire parent au path pour importer les modules
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))


class MatchAnalyzer:
    """Analyseur de match pour Zapier"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.matchday = config['matchday']
        self.team_name = config['team_name']
        self.sources = config['sources']
        self.options = config.get('options', {})
        self.callback_url = config.get('callback_url')
        
        # Chemins de travail
        self.workspace = repo_root / '.memory-bank' / 'competitions' / 'analysis' / self.matchday
        self.output_dir = repo_root / 'completed-tasks' / 'competitions' / 'match_reports' / self.matchday
        
        # Créer les répertoires
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            'status': 'success',
            'matchday': self.matchday,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'results': {},
            'artifacts': {},
            'sources': []
        }
    
    def validate_input(self) -> bool:
        """Valide les données d'entrée"""
        if not self.sources.get('screenshots'):
            raise ValueError("Au moins une capture d'écran est requise")
        
        # Valider le format de date
        try:
            datetime.strptime(self.matchday, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Format de date invalide: {self.matchday}. Attendu: YYYY-MM-DD")
        
        return True
    
    def step1_provision(self) -> None:
        """Étape 1: Provision - Créer l'espace de travail et copier les sources"""
        print(f"📁 Provision: Création de l'espace de travail {self.workspace}")
        
        # Télécharger/copier les sources
        # Note: Dans un contexte réel, vous téléchargeriez les fichiers depuis les URLs
        # Pour l'instant, nous simulons
        
        self.results['sources'].append(str(self.workspace))
    
    def step2_extraction(self) -> Dict[str, Any]:
        """Étape 2: Extraction - Générer le JSON du match
        
        Note: Cette étape nécessiterait normalement l'agent performance-analysis
        avec une capacité de vision pour analyser les captures d'écran.
        Dans le contexte Zapier, cela pourrait être:
        - Un appel à une API de vision (GPT-4 Vision, Google Vision, etc.)
        - Une validation manuelle via formulaire Zapier
        - Un fichier JSON déjà préparé
        """
        print(f"🔍 Extraction: Analyse des captures d'écran...")
        
        json_file = self.workspace / f"match_{self.matchday}.json"
        
        # Si un fichier JSON source est fourni, l'utiliser
        if self.sources.get('json_file'):
            print(f"  → Utilisation du JSON source fourni")
            # Dans un vrai contexte, télécharger depuis l'URL
            # Pour l'instant, on suppose qu'il existe
            self.results['sources'].append(self.sources['json_file'])
        else:
            print(f"  → Génération du JSON depuis les captures (nécessite agent vision)")
            # Ici, vous appelleriez l'agent de vision
            # Pour le moment, créer un template
            match_data = {
                "match_header": f"{self.team_name} vs Adversaire {self.matchday}",
                "our_team": self.team_name,
                "events": []
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(match_data, f, indent=2, ensure_ascii=False)
        
        self.results['artifacts']['json_file'] = str(json_file)
        return match_data
    
    def step3_classification(self, match_data: Dict[str, Any]) -> None:
        """Étape 3: Classification - Exécuter parse_timeline.py"""
        print(f"📊 Classification: Analyse des événements...")
        
        json_file = self.results['artifacts']['json_file']
        parse_script = repo_root / 'tools' / 'parse_timeline.py'
        
        if not parse_script.exists():
            print(f"  ⚠️ Script parse_timeline.py introuvable")
            return
        
        try:
            result = subprocess.run(
                ['python', str(parse_script), json_file],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"  ✓ Classification réussie")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Erreur lors de la classification: {e.stderr}")
            self.results['status'] = 'partial'
            if 'error' not in self.results:
                self.results['error'] = {}
            self.results['error']['classification'] = e.stderr
    
    def step4_build_summary(self) -> None:
        """Étape 4: Construire le match_summary.md"""
        print(f"📝 Build: Génération du match_summary.md...")
        
        summary_file = self.workspace / f"match_summary.md"
        
        # Créer un summary basique
        # Dans un vrai contexte, cela serait généré par l'agent
        summary_content = f"""# Match Summary - {self.matchday}

## Match
{self.team_name}

## Date
{self.matchday}

## Statut
Analysé via Zapier

## Sources
- Captures d'écran: {len(self.sources.get('screenshots', []))}
- JSON: {self.results['artifacts'].get('json_file', 'N/A')}
"""
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        self.results['artifacts']['summary_file'] = str(summary_file)
        print(f"  ✓ Summary généré: {summary_file}")
    
    def step5_validate_template(self) -> bool:
        """Étape 5: Valider le template si demandé"""
        if not self.options.get('validate_template', True):
            return True
        
        print(f"✅ Validation: Vérification du template...")
        
        validator_script = repo_root / 'tools' / 'report_template_validator.py'
        summary_file = self.results['artifacts'].get('summary_file')
        
        if not validator_script.exists() or not summary_file:
            print(f"  ⚠️ Validation ignorée (script ou fichier manquant)")
            return True
        
        try:
            result = subprocess.run(
                ['python', str(validator_script), summary_file],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"  ✓ Template valide")
            if 'results' not in self.results:
                self.results['results'] = {}
            if 'validation' not in self.results['results']:
                self.results['results']['validation'] = {}
            self.results['results']['validation']['template_valid'] = True
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Template invalide: {e.stderr}")
            if 'results' not in self.results:
                self.results['results'] = {}
            if 'validation' not in self.results['results']:
                self.results['results']['validation'] = {}
            self.results['results']['validation']['template_valid'] = False
            self.results['results']['validation']['warnings'] = [e.stderr]
            return False
    
    def step6_generate_full_report(self) -> None:
        """Étape 6: Générer le rapport complet si demandé"""
        if not self.options.get('generate_full_report', True):
            return
        
        print(f"📄 Rapport: Génération du rapport complet...")
        
        report_file = self.output_dir / 'rapport_analyse_complete.md'
        template_file = repo_root / 'templates' / 'rapport_analyse_complete.md'
        
        # Copier ou générer le rapport
        # Dans un vrai contexte, cela serait fait par l'agent
        report_content = f"""# Rapport d'Analyse Complète - {self.matchday}

## Équipe
{self.team_name}

## Date
{self.matchday}

## Analyse
Rapport généré automatiquement via Zapier

## Sources
{chr(10).join(f'- {s}' for s in self.results['sources'])}

---
*Généré le {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC*
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.results['artifacts']['report_file'] = str(report_file)
        print(f"  ✓ Rapport complet généré: {report_file}")
    
    def step7_archive(self) -> None:
        """Étape 7: Archiver si demandé"""
        if not self.options.get('auto_archive', False):
            return
        
        print(f"📦 Archive: Archivage des artefacts...")
        
        archive_script = repo_root / 'tools' / 'archive_match.py'
        
        if not archive_script.exists():
            print(f"  ⚠️ Script archive_match.py introuvable")
            return
        
        try:
            result = subprocess.run(
                ['python', str(archive_script), self.matchday],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"  ✓ Archivage réussi")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️ Erreur lors de l'archivage: {e.stderr}")
    
    def notify_callback(self) -> None:
        """Envoyer une notification au webhook de callback Zapier"""
        if not self.callback_url:
            return
        
        print(f"🔔 Callback: Notification à {self.callback_url}")
        
        # Dans un contexte réel, faire un POST HTTP
        # import requests
        # requests.post(self.callback_url, json=self.results)
        
        print(f"  ✓ Notification envoyée (simulé)")
    
    def run(self) -> Dict[str, Any]:
        """Exécuter le pipeline complet"""
        try:
            print(f"\n{'='*60}")
            print(f"🏃 Démarrage de l'analyse du match {self.matchday}")
            print(f"{'='*60}\n")
            
            self.validate_input()
            self.step1_provision()
            match_data = self.step2_extraction()
            self.step3_classification(match_data)
            self.step4_build_summary()
            self.step5_validate_template()
            self.step6_generate_full_report()
            self.step7_archive()
            self.notify_callback()
            
            print(f"\n{'='*60}")
            print(f"✅ Analyse complétée avec succès!")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"❌ Erreur lors de l'analyse: {str(e)}")
            print(f"{'='*60}\n")
            
            self.results['status'] = 'error'
            self.results['error'] = {
                'code': 'ANALYSIS_ERROR',
                'message': str(e),
                'details': {}
            }
        
        return self.results


def main():
    """Point d'entrée pour Zapier"""
    # Lire la configuration depuis stdin (fournie par Zapier)
    if len(sys.argv) > 1:
        # Mode fichier
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        # Mode stdin
        config = json.load(sys.stdin)
    
    analyzer = MatchAnalyzer(config)
    results = analyzer.run()
    
    # Retourner les résultats en JSON (pour Zapier)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Code de sortie
    sys.exit(0 if results['status'] == 'success' else 1)


if __name__ == '__main__':
    main()
