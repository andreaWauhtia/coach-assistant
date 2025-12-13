# Zapier Integration - Coach Assistant

Ce dossier contient l'intégration Zapier pour le système Coach Assistant, permettant d'automatiser les workflows d'analyse sportive via des webhooks et des actions.

## 📁 Structure

```
zapier/
├── config/
│   └── zapier.config.json          # Configuration principale Zapier
├── schemas/
│   ├── match_input.json            # Schéma d'entrée pour analyse de match
│   ├── match_output.json           # Schéma de sortie pour analyse de match
│   ├── player_input.json           # Schéma d'entrée pour scout joueur
│   ├── player_output.json          # Schéma de sortie pour scout joueur
│   ├── training_input.json         # Schéma d'entrée pour analyse d'entraînement
│   └── training_output.json        # Schéma de sortie pour analyse d'entraînement
├── actions/
│   ├── analyze_match.py            # Action: Analyser un match
│   ├── scout_player.py             # Action: Scout de joueur
│   └── analyze_training.py         # Action: Analyser un entraînement
├── webhooks/
│   └── (à implémenter selon votre serveur)
└── README.md                       # Ce fichier
```

## 🚀 Actions Disponibles

### 1. Analyze Match (`analyze_match`)
Pipeline complet d'analyse de match avec extraction, classification et génération de rapports.

**Exemple d'utilisation:**
```bash
python zapier/actions/analyze_match.py config.json
```

**Fichier config.json:**
```json
{
  "matchday": "2025-10-16",
  "team_name": "USAO U8",
  "sources": {
    "screenshots": [
      "https://example.com/screen1.png",
      "https://example.com/screen2.png"
    ]
  },
  "options": {
    "auto_archive": false,
    "generate_full_report": true,
    "validate_template": true
  },
  "callback_url": "https://hooks.zapier.com/hooks/catch/YOUR_WEBHOOK"
}
```

### 2. Scout Player (`scout_player`)
Mise à jour et analyse de fiche joueur à partir de multiples sources.

**Exemple d'utilisation:**
```bash
python zapier/actions/scout_player.py config.json
```

**Fichier config.json:**
```json
{
  "player_name": "Jean Dupont",
  "sources": {
    "roster_files": ["completed-tasks/roster/roster.json"],
    "training_reports": ["trainings/report/training_2025-10-01.md"],
    "competition_reports": ["completed-tasks/competitions/match_reports/2025-10-16/rapport_analyse_complete.md"]
  },
  "update_mode": "merge",
  "callback_url": "https://hooks.zapier.com/hooks/catch/YOUR_WEBHOOK"
}
```

### 3. Analyze Training (`analyze_training`)
Génération de rapport d'entraînement avec statistiques et recommandations.

**Exemple d'utilisation:**
```bash
python zapier/actions/analyze_training.py config.json
```

**Fichier config.json:**
```json
{
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
      "name": "Jeu réduit",
      "duration": 30,
      "participants": ["Jean", "Marie", "Pierre", "Sophie"],
      "notes": "Très bon engagement"
    }
  ],
  "attendance": ["Jean", "Marie", "Pierre", "Sophie"],
  "notes": "Session productive avec une bonne ambiance",
  "callback_url": "https://hooks.zapier.com/hooks/catch/YOUR_WEBHOOK"
}
```

## 🔗 Intégration avec Zapier

### Triggers (Déclencheurs)

1. **New Match Data** - `/webhooks/match/new`
   - Déclenché quand un nouveau match doit être analysé
   
2. **New Training Session** - `/webhooks/training/new`
   - Déclenché quand une nouvelle session d'entraînement est créée
   
3. **Player Performance Update** - `/webhooks/player/update`
   - Déclenché quand les performances d'un joueur sont mises à jour

### Actions (dans Zapier)

Pour chaque action Python ci-dessus, vous pouvez créer une action Zapier personnalisée:

1. Dans Zapier, créez une **Webhooks by Zapier** action
2. Configurez-la en mode **POST**
3. URL: L'endpoint de votre serveur qui exécutera le script Python
4. Payload: Utilisez les schémas JSON fournis dans `schemas/`

### Configuration de l'authentification

L'intégration utilise une clé API dans le header:
```
X-Coach-Assistant-API-Key: YOUR_API_KEY
```

## 🛠️ Configuration du Serveur

Pour rendre ces actions accessibles via Zapier, vous devez:

1. **Héberger un serveur web** (Flask, FastAPI, Express, etc.)
2. **Créer des endpoints** qui appellent les scripts Python
3. **Gérer l'authentification** via la clé API

### Exemple avec Flask:

```python
from flask import Flask, request, jsonify
import subprocess
import json

app = Flask(__name__)

API_KEY = "your-secret-api-key"

def verify_api_key():
    key = request.headers.get('X-Coach-Assistant-API-Key')
    return key == API_KEY

@app.route('/actions/analyze-match', methods=['POST'])
def analyze_match():
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    
    # Sauvegarder en fichier temporaire
    with open('/tmp/match_config.json', 'w') as f:
        json.dump(data, f)
    
    # Exécuter le script
    result = subprocess.run(
        ['python', 'zapier/actions/analyze_match.py', '/tmp/match_config.json'],
        capture_output=True,
        text=True
    )
    
    return jsonify(json.loads(result.stdout))

@app.route('/actions/scout-player', methods=['POST'])
def scout_player():
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    
    with open('/tmp/player_config.json', 'w') as f:
        json.dump(data, f)
    
    result = subprocess.run(
        ['python', 'zapier/actions/scout_player.py', '/tmp/player_config.json'],
        capture_output=True,
        text=True
    )
    
    return jsonify(json.loads(result.stdout))

@app.route('/actions/analyze-training', methods=['POST'])
def analyze_training():
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    
    with open('/tmp/training_config.json', 'w') as f:
        json.dump(data, f)
    
    result = subprocess.run(
        ['python', 'zapier/actions/analyze_training.py', '/tmp/training_config.json'],
        capture_output=True,
        text=True
    )
    
    return jsonify(json.loads(result.stdout))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 📊 Schémas de Données

Tous les schémas JSON sont disponibles dans le dossier `schemas/` et suivent la spécification JSON Schema Draft 7.

### Validation des schémas

Vous pouvez valider vos données d'entrée avec:

```python
import json
import jsonschema

# Charger le schéma
with open('zapier/schemas/match_input.json') as f:
    schema = json.load(f)

# Charger vos données
with open('my_data.json') as f:
    data = json.load(f)

# Valider
try:
    jsonschema.validate(instance=data, schema=schema)
    print("✓ Données valides")
except jsonschema.exceptions.ValidationError as e:
    print(f"✗ Erreur de validation: {e.message}")
```

## 🔄 Migration depuis l'ancien système

L'ancienne structure basée sur `.github/chatmodes` et `.github/agents` est préservée. Cette nouvelle structure Zapier:

- ✅ Utilise les mêmes scripts dans `tools/`
- ✅ Maintient la même logique métier
- ✅ Ajoute une couche d'automatisation via webhooks
- ✅ Fournit des sorties JSON standardisées
- ✅ Supporte les callbacks pour les notifications

## 🧪 Tests

Pour tester une action localement:

```bash
# Créer un fichier de test
cat > test_match.json << EOF
{
  "matchday": "2025-10-16",
  "team_name": "USAO U8",
  "sources": {
    "screenshots": ["test.png"]
  }
}
EOF

# Exécuter l'action
python zapier/actions/analyze_match.py test_match.json
```

## 📝 Logs et Debugging

Chaque action affiche des logs détaillés dans stdout:
- 📁 Provision
- 🔍 Extraction
- 📊 Classification
- 📝 Build
- ✅ Validation
- 📄 Rapport
- 📦 Archive
- 🔔 Callback

## 🚧 TODO

- [ ] Implémenter les webhooks réels
- [ ] Ajouter plus d'actions (plan-session, review-performance, etc.)
- [ ] Créer des tests unitaires
- [ ] Ajouter la gestion d'erreurs avancée
- [ ] Implémenter le retry mechanism
- [ ] Ajouter des métriques et monitoring

## 📚 Ressources

- [Documentation Zapier Webhooks](https://zapier.com/help/doc/how-use-webhooks-zapier)
- [JSON Schema](https://json-schema.org/)
- [Python subprocess](https://docs.python.org/3/library/subprocess.html)

## 🤝 Support

Pour toute question ou problème, vérifiez:
1. Les logs générés par les actions
2. La validation des schémas JSON
3. L'authentification API
4. La connectivité réseau pour les callbacks
