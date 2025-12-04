#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Action Zapier: Analyze Training
Génération de rapport d'entraînement compatible Zapier
"""
import json
import sys
import io
from pathlib import Path
from datetime import datetime, timezone

# Fix encodage UTF-8 pour Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from typing import Dict, Any, List

repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root))


class TrainingAnalyzer:
    """Analyseur d'entraînement pour Zapier"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.date = config['date']
        self.team_name = config['team_name']
        self.session_type = config.get('session_type', 'training')
        self.drills = config.get('drills', [])
        self.attendance = config.get('attendance', [])
        self.notes = config.get('notes', '')
        self.callback_url = config.get('callback_url')
        
        # Chemins
        self.reports_dir = repo_root / 'trainings' / 'report'
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            'status': 'success',
            'date': self.date,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'report': {}
        }
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """Calcule les statistiques de la session"""
        total_duration = sum(drill.get('duration', 0) for drill in self.drills)
        drills_completed = len(self.drills)
        
        # Taux de présence (si on a une liste de référence)
        # Pour l'instant, on utilise le nombre de participants
        attendance_rate = len(self.attendance) if self.attendance else 0
        
        return {
            'total_duration': total_duration,
            'drills_completed': drills_completed,
            'attendance_rate': attendance_rate
        }
    
    def generate_summary(self, stats: Dict[str, Any]) -> str:
        """Génère un résumé textuel de la session"""
        summary_parts = [
            f"Session de {self.session_type} du {self.date} pour {self.team_name}.",
            f"{stats['drills_completed']} exercices réalisés pour une durée totale de {stats['total_duration']} minutes.",
            f"{stats['attendance_rate']} joueurs présents."
        ]
        
        if self.notes:
            summary_parts.append(f"Notes: {self.notes}")
        
        return ' '.join(summary_parts)
    
    def extract_highlights(self) -> List[str]:
        """Extrait les points saillants de la session"""
        highlights = []
        
        # Analyser les drills pour trouver les points remarquables
        for drill in self.drills:
            if drill.get('notes'):
                highlights.append(f"{drill['name']}: {drill['notes']}")
        
        # Si notes générales
        if self.notes and len(self.notes) > 50:
            highlights.append(f"Observation générale: {self.notes[:100]}...")
        
        return highlights[:5]  # Top 5
    
    def generate_recommendations(self) -> List[str]:
        """Génère des recommandations pour la prochaine session"""
        recommendations = []
        
        stats = self.calculate_statistics()
        
        # Recommandations basées sur la durée
        if stats['total_duration'] < 60:
            recommendations.append("Considérer une session plus longue pour la prochaine fois")
        elif stats['total_duration'] > 120:
            recommendations.append("Session assez intensive, prévoir un jour de récupération")
        
        # Recommandations basées sur les drills
        if stats['drills_completed'] < 3:
            recommendations.append("Diversifier les exercices pour maintenir l'engagement")
        
        # Recommandations basées sur la présence
        if stats['attendance_rate'] < 10:
            recommendations.append("Améliorer la communication pour augmenter la participation")
        
        return recommendations
    
    def generate_markdown_report(self, stats: Dict[str, Any]) -> str:
        """Génère le rapport au format Markdown"""
        highlights = self.extract_highlights()
        recommendations = self.generate_recommendations()
        summary = self.generate_summary(stats)
        
        md = f"""# Rapport d'Entraînement - {self.date}

## Équipe
{self.team_name}

## Type de Session
{self.session_type.title()}

## Résumé
{summary}

## Statistiques
- **Durée totale**: {stats['total_duration']} minutes
- **Exercices réalisés**: {stats['drills_completed']}
- **Joueurs présents**: {stats['attendance_rate']}

## Exercices Détaillés
"""
        
        for i, drill in enumerate(self.drills, 1):
            md += f"\n### {i}. {drill.get('name', 'Exercice sans nom')}\n"
            md += f"- **Durée**: {drill.get('duration', 'N/A')} minutes\n"
            
            participants = drill.get('participants', [])
            if participants:
                md += f"- **Participants**: {', '.join(participants)}\n"
            
            notes = drill.get('notes')
            if notes:
                md += f"- **Notes**: {notes}\n"
        
        md += "\n## Points Saillants\n"
        if highlights:
            for highlight in highlights:
                md += f"- {highlight}\n"
        else:
            md += "Aucun point saillant particulier\n"
        
        md += "\n## Recommandations\n"
        if recommendations:
            for rec in recommendations:
                md += f"- {rec}\n"
        else:
            md += "Continuer sur cette lancée\n"
        
        md += "\n## Présences\n"
        if self.attendance:
            for player in sorted(self.attendance):
                md += f"- {player}\n"
        else:
            md += "Liste de présence non fournie\n"
        
        md += f"\n---\n*Généré le {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC via Zapier*\n"
        
        return md
    
    def save_report(self, report_content: str) -> str:
        """Sauvegarde le rapport"""
        report_file = self.reports_dir / f"training_{self.date}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(report_file)
    
    def notify_callback(self) -> None:
        """Notification vers webhook Zapier"""
        if not self.callback_url:
            return
        
        print(f"🔔 Callback: Notification à {self.callback_url}")
        # import requests
        # requests.post(self.callback_url, json=self.results)
    
    def run(self) -> Dict[str, Any]:
        """Exécuter l'analyse de l'entraînement"""
        try:
            print(f"\n{'='*60}")
            print(f"📊 Analyse de l'entraînement du {self.date}")
            print(f"{'='*60}\n")
            
            # Calculer les statistiques
            stats = self.calculate_statistics()
            
            # Générer le résumé et les recommandations
            summary = self.generate_summary(stats)
            highlights = self.extract_highlights()
            recommendations = self.generate_recommendations()
            
            # Construire le rapport
            self.results['report'] = {
                'summary': summary,
                'attendance_rate': stats['attendance_rate'],
                'drills_completed': stats['drills_completed'],
                'total_duration': stats['total_duration'],
                'highlights': highlights,
                'recommendations': recommendations
            }
            
            # Générer le rapport Markdown
            report_content = self.generate_markdown_report(stats)
            report_file = self.save_report(report_content)
            
            self.results['report_file'] = report_file
            
            print(f"✓ Rapport généré: {report_file}")
            
            self.notify_callback()
            
            print(f"\n{'='*60}")
            print(f"✅ Analyse d'entraînement complétée!")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"\n❌ Erreur: {str(e)}\n")
            self.results['status'] = 'error'
            self.results['error'] = {
                'code': 'TRAINING_ANALYSIS_ERROR',
                'message': str(e)
            }
        
        return self.results


def main():
    """Point d'entrée pour Zapier"""
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = json.load(sys.stdin)
    
    analyzer = TrainingAnalyzer(config)
    results = analyzer.run()
    
    print(json.dumps(results, indent=2, ensure_ascii=False))
    sys.exit(0 if results['status'] == 'success' else 1)


if __name__ == '__main__':
    main()
