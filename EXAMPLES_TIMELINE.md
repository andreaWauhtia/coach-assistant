# Exemples d'utilisation du parser timeline

## Exemple 1 : Match simple avec les types de tirs

**Image timeline :**
```
                11:35
    R.St.FC.Bouillon    4-12    USAO U8
           ↓
        5'  ←→ Tir arrêté (Lilou Douny)
        4'  ←  But (Nestor Arnould) + Passe
        3'  ←  Tir à côté (Nestor Arnould)
        3'  ←  Tir à côté (Nestor Arnould)
        2'  ←  Tir à côté (Nestor Arnould)
```

**JSON d'entrée :**
```json
{
  "match_header": "R.St.FC.Bouillon 4-12 USAO U8 2025/2026",
  "events": [
    {"minute": 5, "type": "Tir arrêté", "player": "Lilou Douny", "side": "right"},
    {"minute": 4, "type": "But", "player": "Nestor Arnould", "side": "left"},
    {"minute": 4, "type": "Passe décisive de Nestor Arnould", "player": null, "side": "left"},
    {"minute": 3, "type": "Tir à côté", "player": "Nestor Arnould", "side": "left"},
    {"minute": 3, "type": "Tir à côté", "player": "Nestor Arnould", "side": "left"},
    {"minute": 2, "type": "Tir à côté", "player": "Nestor Arnould", "side": "left"}
  ]
}
```

**CSV généré :**
```
minute,type,player,side,team,classification,inferred_actions,confidence
5,Tir arrêté,Lilou Douny,right,opponent,shoot,frappe_créée,1.00
4,But,Nestor Arnould,left,us,goal,,1.00
4,Passe décisive de Nestor Arnould,,left,us,,,0.50
3,Tir à côté,Nestor Arnould,left,us,shoot,,1.00
3,Tir à côté,Nestor Arnould,left,us,shoot,,1.00
2,Tir à côté,Nestor Arnould,left,us,shoot,,1.00
```

**Interprétation :**
- ✅ **Notre équipe (gauche)** : 1 but + 3 tirs manqués = 4 tirs totaux
- ✅ **Adversaire (droite)** : 1 arrêt (déduit = 1 tir créé par nous)
- 💡 La ligne "Passe décisive" n'a pas de classification, mais c'est normal (événement informatif)

---

## Exemple 2 : Match avec défense (arrêts)

**Scénario :** Vous subissez des frappes et vous les arrêtez.

**JSON d'entrée :**
```json
{
  "match_header": "Équipe A 0-2 Équipe B 2024/2025",
  "events": [
    {"minute": 60, "type": "But", "player": "Joueur Adverse", "side": "right"},
    {"minute": 50, "type": "Arrêt", "player": "Notre Gardien", "side": "left"},
    {"minute": 45, "type": "But", "player": "Joueur Adverse 2", "side": "right"},
    {"minute": 30, "type": "Tir arrêté", "player": "Notre Gardien", "side": "left"}
  ]
}
```

**CSV généré :**
```
minute,type,player,side,team,classification,inferred_actions,confidence
60,But,Joueur Adverse,right,opponent,goal,,1.00
50,Arrêt,Notre Gardien,left,us,shoot,frappe_subite,1.00
45,But,Joueur Adverse 2,right,opponent,goal,,1.00
30,Tir arrêté,Notre Gardien,left,us,shoot,frappe_subite,1.00
```

**Analyse :**
- Nous avons subi 4 frappes (2 buts + 2 arrêts)
- Nous n'avons rien tiré
- L'équipe A a dominé complètement (2-0)
- Les 2 "arrêts" sont marqués `frappe_subite` = nous avons vraiment subi ces frappes

---

## Exemple 3 : Mix offensif/défensif

**JSON d'entrée :**
```json
{
  "match_header": "Paris 3-2 Lyon 2024/2025",
  "events": [
    {"minute": 90, "type": "But", "player": "Benzema", "side": "right"},
    {"minute": 85, "type": "Arrêt", "player": "Areola", "side": "left"},
    {"minute": 80, "type": "But", "player": "Messi", "side": "left"},
    {"minute": 70, "type": "Tir à côté", "player": "Messi", "side": "left"},
    {"minute": 65, "type": "But", "player": "Mbappé", "side": "left"},
    {"minute": 50, "type": "Tir à côté", "player": "Benzema", "side": "right"},
    {"minute": 45, "type": "But", "player": "Benzema", "side": "right"}
  ]
}
```

**CSV généré :**
```
minute,type,player,side,team,classification,inferred_actions,confidence
90,But,Benzema,right,opponent,goal,,1.00
85,Arrêt,Areola,left,us,shoot,frappe_subite,1.00
80,But,Messi,left,us,goal,,1.00
70,Tir à côté,Messi,left,us,shoot,,1.00
65,But,Mbappé,left,us,goal,,1.00
50,Tir à côté,Benzema,right,opponent,shoot,,1.00
45,But,Benzema,right,opponent,goal,,1.00
```

**Statistiques générées automatiquement :**
- **Paris** : 3 buts, 4 tirs (dont 1 arrêt, 1 à côté)
- **Lyon** : 2 buts, 3 tirs (dont 1 à côté)
- **Tirs que nous avons subis** : 3 (2 buts + 1 arrêt)
- **Tirs que nous avons créés** : 1 (Areola a dû intervenir)

---

## Exemple 4 : Éléments ignorés / non-classifiés

**JSON d'entrée :**
```json
{
  "match_header": "Équipe A 1-0 Équipe B 2024/2025",
  "events": [
    {"minute": 45, "type": "But", "player": "Marchand", "side": "left"},
    {"minute": 40, "type": "Carton Jaune", "player": "Joueur B", "side": "right"},
    {"minute": 30, "type": "Blessé", "player": "Joueur A", "side": "left"},
    {"minute": 20, "type": "Remplacement", "player": "Entrant vs Sortant", "side": "right"},
    {"minute": 10, "type": "Action inconnue", "player": "Quelconque", "side": "left"}
  ]
}
```

**CSV généré :**
```
minute,type,player,side,team,classification,inferred_actions,confidence
45,But,Marchand,left,us,goal,,1.00
40,Carton Jaune,Joueur B,right,opponent,card,,0.75
30,Blessé,Joueur A,left,us,injury,,0.75
20,Remplacement,Entrant vs Sortant,right,opponent,substitution,,0.75
10,Action inconnue,Quelconque,left,us,,,1.00
```

**Notes :**
- ✅ But classifié comme "goal"
- ✅ Carton jaune classifié comme "card"
- ✅ Blessé classifié comme "injury"
- ✅ Remplacement classifié comme "substitution"
- ⚠️ "Action inconnue" : pas de classification (confiance 1.0 car joueur présent mais type inconnu)

---

## Mode interactif - Transcription manuelle

Quand vous exécutez :
```bash
python tools/parse_timeline.py --interactive
```

Le script vous guide :
```
=== INTERACTIVE MODE ===

Enter match header (e.g., 'Team1 4-12 Team2 2025/2026'): Paris 3-2 Lyon 2024/2025
   👥 Our team: Paris
   👥 Opponent: Lyon

Enter events one by one (leave minute empty to finish):
Format: minute type player side
  minute: number (1-90)
  type: But, Carton Jaune, Carton Rouge, Remplacement, Arrêt, Tir à côté, Poteau, Transversale, Tir arrêté, Blessé
  player: name or empty
  side: left or right

Minute (or empty to finish): 45
Event type: But
Player (optional): Mbappé
Side (left/right): left
✅ Event added

Minute (or empty to finish): 30
Event type: Arrêt
Player (optional): Areola
Side (left/right): left
✅ Event added

Minute (or empty to finish): 
Processing 2 events...
✅ CSV exported: output/parsed_by_side.csv
✅ Report exported: output/2025-11-07.md
```

---

## Récapitulatif de la logique de classification

### Types d'événements

| Type | Classification | Notes |
|------|-----------------|-------|
| But | goal | Direct |
| Tir à côté | shoot | Tir manqué |
| Poteau | shoot | Tir sur le poteau |
| Transversale | shoot | Tir sur la transversale |
| Arrêt | shoot + frappe_subite/créée | Si nous: frappe_subite, si adversaire: frappe_créée |
| Tir arrêté | shoot + frappe_subite/créée | Même logique que Arrêt |
| Carton Jaune | card | Avertissement |
| Carton Rouge | card | Expulsion |
| Remplacement | substitution | Changement |
| Blessé | injury | Joueur blessé |
| Autres | (non-classifié) | Événements informatifs |

### Règle d'inférence

```
SI (nous avons un Arrêt OU nous avons un Tir arrêté)
  ALORS inférer: frappe_subite
  (= l'adversaire a tiré et nous avons défendu)

SI (adversaire a un Arrêt OU adversaire a un Tir arrêté)
  ALORS inférer: frappe_créée
  (= nous avons tiré et l'adversaire a défendu)
```

Cette logique permet d'inférer les frappes qui ne sont pas explicitement rapportées dans la timeline !
