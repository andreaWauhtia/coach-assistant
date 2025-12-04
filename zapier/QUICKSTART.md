# 🚀 Quick Start - Zapier Integration

Guide rapide pour démarrer avec l'intégration Zapier du Coach Assistant.

## ⚡ Installation Rapide (5 minutes)

### 1. Installer les dépendances

```bash
cd zapier
pip install -r requirements.txt
```

### 2. Configurer les variables d'environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer le fichier .env et changer la clé API
# COACH_ASSISTANT_API_KEY=votre-clé-secrète-ici
```

### 3. Tester les actions

```bash
# Lancer les tests
python test_actions.py
```

Vous devriez voir:
```
============================================================
✅ TOUS LES TESTS ONT RÉUSSI
============================================================
```

### 4. Démarrer le serveur

```bash
# Mode développement
python server.py

# Le serveur démarre sur http://localhost:5000
```

Ouvrir dans votre navigateur: http://localhost:5000

Vous devriez voir la page d'accueil de l'API.

## 🧪 Tester avec curl

### Test de l'endpoint d'analyse de match

```bash
curl -X POST http://localhost:5000/actions/analyze-match \
  -H "Content-Type: application/json" \
  -H "X-Coach-Assistant-API-Key: your-secret-api-key-here" \
  -d '{
    "matchday": "2025-10-16",
    "team_name": "USAO U8",
    "sources": {
      "screenshots": ["test1.png", "test2.png"]
    },
    "options": {
      "auto_archive": false,
      "generate_full_report": true
    }
  }'
```

### Test de l'endpoint scout joueur

```bash
curl -X POST http://localhost:5000/actions/scout-player \
  -H "Content-Type: application/json" \
  -H "X-Coach-Assistant-API-Key: your-secret-api-key-here" \
  -d '{
    "player_name": "Jean Dupont"
  }'
```

### Test de l'endpoint analyse d'entraînement

```bash
curl -X POST http://localhost:5000/actions/analyze-training \
  -H "Content-Type: application/json" \
  -H "X-Coach-Assistant-API-Key: your-secret-api-key-here" \
  -d '{
    "date": "2025-10-20",
    "team_name": "USAO U8",
    "drills": [
      {
        "name": "Passe et contrôle",
        "duration": 20
      }
    ],
    "attendance": ["Jean", "Marie"]
  }'
```

## 🌐 Connexion à Zapier (10 minutes)

### Option 1: Webhooks by Zapier (Recommandé pour commencer)

1. **Créer un nouveau Zap** dans Zapier
2. **Trigger**: Choisir un déclencheur (par ex: "New Row in Google Sheets")
3. **Action**: Choisir "Webhooks by Zapier"
4. Configurer:
   - **Event**: POST
   - **URL**: `https://votre-serveur.com/actions/analyze-match`
   - **Headers**: 
     ```
     X-Coach-Assistant-API-Key: your-secret-api-key-here
     Content-Type: application/json
     ```
   - **Payload Type**: JSON
   - **Data**: Mapper les champs du trigger aux champs attendus

### Option 2: ngrok pour tester localement

Si vous n'avez pas encore de serveur public:

```bash
# Installer ngrok: https://ngrok.com/download

# Lancer ngrok sur le port 5000
ngrok http 5000

# Utiliser l'URL fournie par ngrok (ex: https://abc123.ngrok.io)
# dans vos Zaps Zapier
```

## 📝 Exemples de Zaps

### Zap 1: Google Form → Analyse de Match

**Trigger**: New Response in Google Forms
**Action**: Webhooks POST

**Mapping**:
```
URL: https://votre-serveur.com/actions/analyze-match

Data:
{
  "matchday": {{Date du match}},
  "team_name": {{Équipe}},
  "sources": {
    "screenshots": [{{Screenshot 1}}, {{Screenshot 2}}]
  },
  "options": {
    "auto_archive": true,
    "generate_full_report": true
  },
  "callback_url": "{{zap_meta_human_now.IFTTT_WEBHOOK_URL}}"
}
```

### Zap 2: Calendrier → Analyse d'Entraînement

**Trigger**: New Event in Google Calendar (1 heure après l'événement)
**Filter**: Événement contient "Entraînement"
**Action**: Webhooks POST

**Mapping**:
```
URL: https://votre-serveur.com/actions/analyze-training

Data:
{
  "date": {{Event Start Date}},
  "team_name": "USAO U8",
  "session_type": "training",
  "notes": {{Event Description}}
}
```

### Zap 3: Mise à Jour Joueur Hebdomadaire

**Trigger**: Schedule (Every Monday 9 AM)
**Action**: Loop (sur liste de joueurs)
  **Sub-Action**: Webhooks POST

**Mapping**:
```
URL: https://votre-serveur.com/actions/scout-player

Data:
{
  "player_name": {{Player Name from List}},
  "update_mode": "merge"
}
```

## 🚀 Déploiement en Production

### Option 1: Heroku (Gratuit)

```bash
# Créer un Procfile
echo "web: python zapier/server.py" > Procfile

# Créer une app Heroku
heroku create coach-assistant-api

# Définir la clé API
heroku config:set COACH_ASSISTANT_API_KEY=votre-clé-secrète

# Déployer
git add .
git commit -m "Add Zapier integration"
git push heroku main

# Votre API est maintenant disponible sur:
# https://coach-assistant-api.herokuapp.com
```

### Option 2: Railway

1. Aller sur [Railway.app](https://railway.app)
2. Créer un nouveau projet
3. Connecter votre repo GitHub
4. Ajouter les variables d'environnement:
   - `COACH_ASSISTANT_API_KEY`
5. Railway détecte automatiquement Python et démarre le serveur

### Option 3: AWS Lambda + API Gateway

(Plus avancé - voir documentation AWS)

## 🔍 Debugging

### Vérifier que le serveur fonctionne

```bash
curl http://localhost:5000/health
```

Devrait retourner:
```json
{
  "status": "healthy",
  "actions_dir": "...",
  "actions_exist": true
}
```

### Voir les logs du serveur

Le serveur Flask affiche des logs détaillés:
```
2025-10-20 10:30:15 - __main__ - INFO - Executing action: analyze_match
2025-10-20 10:30:45 - __main__ - INFO - Action completed with status: success
```

### Tester une action directement

Sans passer par le serveur:

```bash
# Créer un fichier de config
cat > test_config.json << EOF
{
  "matchday": "2025-10-16",
  "team_name": "USAO U8",
  "sources": {"screenshots": []}
}
EOF

# Exécuter l'action directement
python zapier/actions/analyze_match.py test_config.json
```

## ✅ Checklist de Démarrage

- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Fichier `.env` créé et configuré
- [ ] Tests passent (`python test_actions.py`)
- [ ] Serveur démarre localement (`python server.py`)
- [ ] Endpoints testés avec curl
- [ ] ngrok installé et testé (si test local)
- [ ] Premier Zap créé dans Zapier
- [ ] Premier test end-to-end réussi
- [ ] API déployée en production
- [ ] Clé API sécurisée changée

## 🆘 Problèmes Courants

### "Action not found"
- Vérifier que les fichiers `.py` existent dans `zapier/actions/`
- Vérifier les permissions d'exécution

### "Unauthorized"
- Vérifier que le header `X-Coach-Assistant-API-Key` est présent
- Vérifier que la clé correspond à celle dans `.env`

### "Timeout"
- Augmenter le timeout dans `server.py` (ligne `timeout=300`)
- Vérifier que les scripts Python ne sont pas bloqués

### Les scripts Python ne s'exécutent pas
- Vérifier que Python est dans le PATH
- Vérifier que les dépendances sont installées
- Vérifier le `repo_root` dans les scripts

## 📚 Prochaines Étapes

1. ✅ Terminer ce Quick Start
2. 📖 Lire `README.md` pour plus de détails
3. 🔄 Lire `MIGRATION.md` pour comprendre la migration
4. 🧪 Créer vos premiers Zaps
5. 📊 Monitor les performances
6. 🚀 Étendre avec de nouvelles actions

---

**Besoin d'aide?** Consultez la documentation complète dans `README.md`
