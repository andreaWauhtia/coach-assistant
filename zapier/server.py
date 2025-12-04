#!/usr/bin/env python3
"""
Flask Server for Zapier Integration
Serveur web exposant les actions Coach Assistant pour Zapier
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import os
from pathlib import Path
import tempfile
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Activer CORS pour Zapier

# Configuration
API_KEY = os.environ.get('COACH_ASSISTANT_API_KEY', 'your-secret-api-key-here')
REPO_ROOT = Path(__file__).resolve().parents[1]

# Vérifier que les actions existent
ACTIONS_DIR = REPO_ROOT / 'zapier' / 'actions'
if not ACTIONS_DIR.exists():
    logger.error(f"Actions directory not found: {ACTIONS_DIR}")
    raise RuntimeError("Actions directory not found")


def verify_api_key():
    """Vérifie la clé API dans le header"""
    key = request.headers.get('X-Coach-Assistant-API-Key')
    if not key:
        logger.warning("API key missing in request")
        return False
    if key != API_KEY:
        logger.warning(f"Invalid API key: {key[:10]}...")
        return False
    return True


def execute_action(action_name: str, config: dict) -> tuple:
    """
    Exécute une action Python avec la configuration fournie
    
    Args:
        action_name: Nom de l'action (sans .py)
        config: Configuration JSON
    
    Returns:
        tuple: (result_dict, status_code)
    """
    action_file = ACTIONS_DIR / f"{action_name}.py"
    
    if not action_file.exists():
        logger.error(f"Action not found: {action_name}")
        return {
            'error': {
                'code': 'ACTION_NOT_FOUND',
                'message': f"Action '{action_name}' not found"
            }
        }, 404
    
    # Créer un fichier temporaire pour la config
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
        config_file = f.name
    
    try:
        logger.info(f"Executing action: {action_name}")
        logger.debug(f"Config: {json.dumps(config, indent=2)}")
        
        # Exécuter le script Python
        result = subprocess.run(
            ['python', str(action_file), config_file],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=300  # 5 minutes max
        )
        
        # Parser la sortie JSON
        try:
            # La dernière ligne devrait être le JSON de résultat
            lines = result.stdout.strip().split('\n')
            # Trouver la ligne JSON (commence par '{')
            json_lines = [line for line in lines if line.strip().startswith('{')]
            if json_lines:
                output = json.loads(json_lines[-1])
            else:
                output = {'status': 'error', 'error': {'message': 'No JSON output'}}
            
            # Ajouter les logs si présents
            log_lines = [line for line in lines if not line.strip().startswith('{')]
            if log_lines:
                output['logs'] = '\n'.join(log_lines)
            
            logger.info(f"Action completed with status: {output.get('status')}")
            
            # Code de retour HTTP selon le statut
            status_code = 200 if output.get('status') == 'success' else 500
            
            return output, status_code
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON output: {e}")
            logger.error(f"stdout: {result.stdout}")
            logger.error(f"stderr: {result.stderr}")
            
            return {
                'status': 'error',
                'error': {
                    'code': 'INVALID_OUTPUT',
                    'message': 'Action returned invalid JSON',
                    'details': {
                        'stdout': result.stdout,
                        'stderr': result.stderr
                    }
                }
            }, 500
            
    except subprocess.TimeoutExpired:
        logger.error(f"Action timeout: {action_name}")
        return {
            'status': 'error',
            'error': {
                'code': 'TIMEOUT',
                'message': 'Action execution timeout (5 minutes)'
            }
        }, 504
        
    except Exception as e:
        logger.error(f"Unexpected error executing action: {e}", exc_info=True)
        return {
            'status': 'error',
            'error': {
                'code': 'EXECUTION_ERROR',
                'message': str(e)
            }
        }, 500
        
    finally:
        # Nettoyer le fichier temporaire
        try:
            os.unlink(config_file)
        except:
            pass


@app.route('/', methods=['GET'])
def index():
    """Page d'accueil avec informations API"""
    return jsonify({
        'name': 'Coach Assistant - Zapier Integration',
        'version': '1.0.0',
        'status': 'running',
        'actions': [
            {
                'id': 'analyze_match',
                'endpoint': '/actions/analyze-match',
                'method': 'POST'
            },
            {
                'id': 'scout_player',
                'endpoint': '/actions/scout-player',
                'method': 'POST'
            },
            {
                'id': 'analyze_training',
                'endpoint': '/actions/analyze-training',
                'method': 'POST'
            }
        ],
        'authentication': {
            'type': 'API Key',
            'header': 'X-Coach-Assistant-API-Key'
        },
        'docs': '/docs'
    })


@app.route('/docs', methods=['GET'])
def docs():
    """Documentation de l'API"""
    readme_file = REPO_ROOT / 'zapier' / 'README.md'
    
    if readme_file.exists():
        with open(readme_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convertir en HTML basique pour affichage
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Coach Assistant API Documentation</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; }}
                pre {{ background: #f4f4f4; padding: 10px; overflow-x: auto; }}
                code {{ background: #f4f4f4; padding: 2px 5px; }}
            </style>
        </head>
        <body>
            <h1>Coach Assistant - Zapier Integration Documentation</h1>
            <pre>{content}</pre>
        </body>
        </html>
        """
        return html
    
    return jsonify({'error': 'Documentation not found'}), 404


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'actions_dir': str(ACTIONS_DIR),
        'actions_exist': ACTIONS_DIR.exists()
    })


# === ACTIONS ===

@app.route('/actions/analyze-match', methods=['POST'])
def analyze_match():
    """Action: Analyze Match"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    config = request.json
    result, status_code = execute_action('analyze_match', config)
    
    return jsonify(result), status_code


@app.route('/actions/scout-player', methods=['POST'])
def scout_player():
    """Action: Scout Player"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    config = request.json
    result, status_code = execute_action('scout_player', config)
    
    return jsonify(result), status_code


@app.route('/actions/analyze-training', methods=['POST'])
def analyze_training():
    """Action: Analyze Training"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    config = request.json
    result, status_code = execute_action('analyze_training', config)
    
    return jsonify(result), status_code


# === WEBHOOKS (pour les triggers) ===

@app.route('/webhooks/match/new', methods=['POST'])
def webhook_match_new():
    """Webhook: New Match Data"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    logger.info(f"Webhook triggered: new match - {data.get('matchday')}")
    
    # Traiter le webhook selon votre logique
    # Par exemple, stocker dans une queue, déclencher une action, etc.
    
    return jsonify({
        'status': 'received',
        'data': data
    }), 200


@app.route('/webhooks/training/new', methods=['POST'])
def webhook_training_new():
    """Webhook: New Training Session"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    logger.info(f"Webhook triggered: new training - {data.get('date')}")
    
    return jsonify({
        'status': 'received',
        'data': data
    }), 200


@app.route('/webhooks/player/update', methods=['POST'])
def webhook_player_update():
    """Webhook: Player Performance Update"""
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    logger.info(f"Webhook triggered: player update - {data.get('player_name')}")
    
    return jsonify({
        'status': 'received',
        'data': data
    }), 200


# === ERROR HANDLERS ===

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': {
            'code': 'NOT_FOUND',
            'message': 'Endpoint not found'
        }
    }), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}", exc_info=True)
    return jsonify({
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': 'Internal server error'
        }
    }), 500


if __name__ == '__main__':
    # Mode développement
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Coach Assistant API server on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"API Key configured: {'Yes' if API_KEY != 'your-secret-api-key-here' else 'No (using default)'}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
