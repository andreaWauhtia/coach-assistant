#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Action Zapier: Scout Player
Mise à jour de fiche joueur compatible Zapier
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


class PlayerScout:
    """Scout de joueur pour Zapier"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.player_name = config['player_name']
        self.player_id = config.get('player_id', self.player_name.lower().replace(' ', '_'))
        self.sources = config.get('sources', {})
        self.update_mode = config.get('update_mode', 'merge')
        self.callback_url = config.get('callback_url')
        
        # Chemins
        self.player_dir = repo_root / 'completed-tasks' / 'roster' / self.player_id
        self.player_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            'status': 'success',
            'player_name': self.player_name,
            'player_id': self.player_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'profile': {},
            'sources_used': []
        }
    
    def load_existing_profile(self) -> Dict[str, Any]:
        """Charge le profil existant si disponible"""
        profile_file = self.player_dir / 'profile.json'
        
        if profile_file.exists():
            with open(profile_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            'personal_info': {
                'name': self.player_name,
                'position': '',
                'age': 0,
                'number': 0
            },
            'statistics': {
                'matches_played': 0,
                'goals': 0,
                'assists': 0,
                'training_attendance': 0.0
            },
            'strengths': [],
            'areas_for_improvement': [],
            'recent_performances': []
        }
    
    def analyze_roster_data(self, profile: Dict[str, Any]) -> None:
        """Analyse les données de roster"""
        roster_files = self.sources.get('roster_files', [])
        
        for roster_file in roster_files:
            roster_path = Path(roster_file)
            if not roster_path.exists():
                print(f"  ⚠️ Fichier roster introuvable: {roster_file}")
                continue
            
            print(f"  → Analyse du roster: {roster_file}")
            self.results['sources_used'].append(roster_file)
            
            # Ici, vous analyseriez le fichier roster
            # Pour l'instant, simuler
    
    def analyze_training_reports(self, profile: Dict[str, Any]) -> None:
        """Analyse les rapports d'entraînement"""
        training_reports = self.sources.get('training_reports', [])
        
        for report in training_reports:
            report_path = Path(report)
            if not report_path.exists():
                print(f"  ⚠️ Rapport d'entraînement introuvable: {report}")
                continue
            
            print(f"  → Analyse du rapport d'entraînement: {report}")
            self.results['sources_used'].append(report)
            
            # Analyser le rapport
            # Extraire la présence, les performances, etc.
    
    def analyze_competition_reports(self, profile: Dict[str, Any]) -> None:
        """Analyse les rapports de compétition"""
        competition_reports = self.sources.get('competition_reports', [])
        
        for report in competition_reports:
            report_path = Path(report)
            if not report_path.exists():
                print(f"  ⚠️ Rapport de compétition introuvable: {report}")
                continue
            
            print(f"  → Analyse du rapport de compétition: {report}")
            self.results['sources_used'].append(report)
            
            # Analyser le rapport de match
            # Extraire buts, passes, performances
    
    def merge_profiles(self, existing: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fusionner les profils selon le mode de mise à jour"""
        if self.update_mode == 'replace':
            return new_data
        elif self.update_mode == 'append':
            # Ajouter aux listes, incrémenter les compteurs
            for key in existing:
                if isinstance(existing[key], list):
                    existing[key].extend(new_data.get(key, []))
                elif isinstance(existing[key], dict):
                    existing[key].update(new_data.get(key, {}))
            return existing
        else:  # merge (default)
            # Fusion intelligente
            for key in new_data:
                if key in existing:
                    if isinstance(existing[key], dict) and isinstance(new_data[key], dict):
                        existing[key].update(new_data[key])
                    elif isinstance(existing[key], list) and isinstance(new_data[key], list):
                        # Éviter les doublons pour les listes
                        existing[key] = list(set(existing[key] + new_data[key]))
                    else:
                        existing[key] = new_data[key]
                else:
                    existing[key] = new_data[key]
            return existing
    
    def save_profile(self, profile: Dict[str, Any]) -> str:
        """Sauvegarde le profil mis à jour"""
        profile_file = self.player_dir / 'profile.json'
        
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        
        # Générer aussi un fichier Markdown
        md_file = self.player_dir / 'profile.md'
        md_content = self.generate_markdown(profile)
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return str(profile_file)
    
    def generate_markdown(self, profile: Dict[str, Any]) -> str:
        """Génère un fichier Markdown du profil"""
        personal = profile.get('personal_info', {})
        stats = profile.get('statistics', {})
        
        md = f"""# Fiche Joueur: {self.player_name}

## Informations Personnelles
- **Nom**: {personal.get('name', self.player_name)}
- **Position**: {personal.get('position', 'Non définie')}
- **Âge**: {personal.get('age', 'N/A')}
- **Numéro**: {personal.get('number', 'N/A')}

## Statistiques
- **Matchs joués**: {stats.get('matches_played', 0)}
- **Buts**: {stats.get('goals', 0)}
- **Passes décisives**: {stats.get('assists', 0)}
- **Assiduité entraînements**: {stats.get('training_attendance', 0):.1f}%

## Points Forts
{chr(10).join(f'- {s}' for s in profile.get('strengths', ['À définir']))}

## Axes d'Amélioration
{chr(10).join(f'- {a}' for a in profile.get('areas_for_improvement', ['À définir']))}

## Performances Récentes
"""
        
        recent = profile.get('recent_performances', [])
        if recent:
            for perf in recent[-5:]:  # 5 dernières performances
                md += f"- **{perf.get('date')}** ({perf.get('event_type')}): {perf.get('rating', 'N/A')}/10\n"
        else:
            md += "Aucune performance enregistrée\n"
        
        md += f"\n---\n*Mis à jour le {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC*\n"
        
        return md
    
    def notify_callback(self) -> None:
        """Notification vers webhook Zapier"""
        if not self.callback_url:
            return
        
        print(f"🔔 Callback: Notification à {self.callback_url}")
        # import requests
        # requests.post(self.callback_url, json=self.results)
    
    def run(self) -> Dict[str, Any]:
        """Exécuter l'analyse du joueur"""
        try:
            print(f"\n{'='*60}")
            print(f"🔍 Scout du joueur: {self.player_name}")
            print(f"{'='*60}\n")
            
            # Charger profil existant
            profile = self.load_existing_profile()
            
            # Analyser les différentes sources
            self.analyze_roster_data(profile)
            self.analyze_training_reports(profile)
            self.analyze_competition_reports(profile)
            
            # Sauvegarder le profil
            profile_file = self.save_profile(profile)
            
            self.results['profile'] = profile
            self.results['profile_file'] = profile_file
            
            self.notify_callback()
            
            print(f"\n{'='*60}")
            print(f"✅ Profil joueur mis à jour!")
            print(f"{'='*60}\n")
            
        except FileNotFoundError:
            self.results['status'] = 'not_found'
            self.results['error'] = {
                'code': 'PLAYER_NOT_FOUND',
                'message': f"Joueur {self.player_name} introuvable"
            }
        except Exception as e:
            self.results['status'] = 'error'
            self.results['error'] = {
                'code': 'SCOUT_ERROR',
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
    
    scout = PlayerScout(config)
    results = scout.run()
    
    print(json.dumps(results, indent=2, ensure_ascii=False))
    sys.exit(0 if results['status'] == 'success' else 1)


if __name__ == '__main__':
    main()
