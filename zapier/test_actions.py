#!/usr/bin/env python3
"""
Tests pour les actions Zapier
Exécuter: python zapier/test_actions.py
"""
import json
import subprocess
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parents[1]
actions_dir = repo_root / 'zapier' / 'actions'

def test_analyze_match():
    """Test de l'action analyze_match"""
    print("\n" + "="*60)
    print("TEST: Analyze Match")
    print("="*60)
    
    config = {
        "matchday": "2025-10-16",
        "team_name": "USAO U8",
        "sources": {
            "screenshots": ["test1.png", "test2.png"]
        },
        "options": {
            "auto_archive": False,
            "generate_full_report": True,
            "validate_template": False
        }
    }
    
    # Créer fichier de config temporaire
    config_file = repo_root / 'test_match_config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    try:
        # Exécuter l'action
        result = subprocess.run(
            ['python', str(actions_dir / 'analyze_match.py'), str(config_file)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=str(repo_root)
        )
        
        print("\nSTDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        # Parser le résultat JSON
        lines = result.stdout.strip().split('\n')
        json_lines = [line for line in lines if line.strip().startswith('{')]
        
        if json_lines:
            output = json.loads(json_lines[-1])
            print("\n" + "="*60)
            print("RÉSULTAT:")
            print(json.dumps(output, indent=2, ensure_ascii=False))
            print("="*60)
            
            return output.get('status') == 'success'
        else:
            print("\n❌ Pas de sortie JSON trouvée")
            return False
            
    finally:
        # Nettoyer
        if config_file.exists():
            config_file.unlink()


def test_scout_player():
    """Test de l'action scout_player"""
    print("\n" + "="*60)
    print("TEST: Scout Player")
    print("="*60)
    
    config = {
        "player_name": "Jean Dupont Test",
        "sources": {
            "roster_files": [],
            "training_reports": [],
            "competition_reports": []
        },
        "update_mode": "merge"
    }
    
    config_file = repo_root / 'test_player_config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    try:
        result = subprocess.run(
            ['python', str(actions_dir / 'scout_player.py'), str(config_file)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=str(repo_root)
        )
        
        print("\nSTDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        lines = result.stdout.strip().split('\n')
        json_lines = [line for line in lines if line.strip().startswith('{')]
        
        if json_lines:
            output = json.loads(json_lines[-1])
            print("\n" + "="*60)
            print("RÉSULTAT:")
            print(json.dumps(output, indent=2, ensure_ascii=False))
            print("="*60)
            
            return output.get('status') in ['success', 'not_found']
        else:
            print("\n❌ Pas de sortie JSON trouvée")
            return False
            
    finally:
        if config_file.exists():
            config_file.unlink()


def test_analyze_training():
    """Test de l'action analyze_training"""
    print("\n" + "="*60)
    print("TEST: Analyze Training")
    print("="*60)
    
    config = {
        "date": "2025-10-20",
        "team_name": "USAO U8",
        "session_type": "training",
        "drills": [
            {
                "name": "Passe et contrôle",
                "duration": 20,
                "participants": ["Jean", "Marie", "Pierre"],
                "notes": "Bonne progression sur le contrôle orienté"
            },
            {
                "name": "Jeu réduit 4v4",
                "duration": 30,
                "participants": ["Jean", "Marie", "Pierre", "Sophie"],
                "notes": "Très bon engagement, bonne lecture du jeu"
            }
        ],
        "attendance": ["Jean", "Marie", "Pierre", "Sophie"],
        "notes": "Excellente session avec une très bonne ambiance"
    }
    
    config_file = repo_root / 'test_training_config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    try:
        result = subprocess.run(
            ['python', str(actions_dir / 'analyze_training.py'), str(config_file)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=str(repo_root)
        )
        
        print("\nSTDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        lines = result.stdout.strip().split('\n')
        json_lines = [line for line in lines if line.strip().startswith('{')]
        
        if json_lines:
            output = json.loads(json_lines[-1])
            print("\n" + "="*60)
            print("RÉSULTAT:")
            print(json.dumps(output, indent=2, ensure_ascii=False))
            print("="*60)
            
            return output.get('status') == 'success'
        else:
            print("\n❌ Pas de sortie JSON trouvée")
            return False
            
    finally:
        if config_file.exists():
            config_file.unlink()


def main():
    """Exécuter tous les tests"""
    print("\n" + "="*60)
    print("TESTS DES ACTIONS ZAPIER")
    print("="*60)
    
    tests = {
        'Analyze Match': test_analyze_match,
        'Scout Player': test_scout_player,
        'Analyze Training': test_analyze_training
    }
    
    results = {}
    
    for name, test_func in tests.items():
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Erreur dans {name}: {e}")
            results[name] = False
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    
    for name, passed in results.items():
        status = "✅ PASSÉ" if passed else "❌ ÉCHOUÉ"
        print(f"{name}: {status}")
    
    # Code de sortie
    all_passed = all(results.values())
    print("\n" + "="*60)
    if all_passed:
        print("✅ TOUS LES TESTS ONT RÉUSSI")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
    print("="*60 + "\n")
    
    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
