#!/usr/bin/env python3
"""
Script to simulate performance analysis from match events JSON and generate a complete report.

Usage: python tools/simulate_performance_analysis.py input.json output.md
"""

import argparse
import json
from collections import defaultdict

def simulate_performance_analysis(json_file, output_file):
    """
    Simulate performance analysis from JSON data and generate markdown report.
    """
    # Charger les données
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extraire les infos de match
    match_info = data.get('match_info', {})
    result = match_info.get('result', 'N/A')
    is_home = match_info.get('is_home', True)
    team_home = "Notre Équipe" if is_home else match_info.get('opponent_name', 'Adversaire')
    team_away = match_info.get('opponent_name', 'Adversaire') if is_home else "Notre Équipe"

    # Initialiser les stats par joueur
    player_stats = defaultdict(lambda: {
        'goals': 0,
        'shots_on_target': 0,
        'shots_off_target': 0,
        'passes': 0,
        'key_passes': 0,
        'tackles': 0,
        'interceptions': 0,
        'duels': 0,
        'duels_won': 0,
        'fouls_suffered': 0,
        'assists': 0,
        'assists_to': defaultdict(int)
    })

    # Stats équipe
    team_stats = {
        'goals_scored': 0,
        'shots_total': 0,
        'shots_off': 0,
        'goals_conceded': 0,
        'shots_conceded': 0,
        'shots_off_conceded': 0
    }

    # Évolution du score
    score_evolution = []
    current_score = [0, 0]  # home, away
    events_by_minute = defaultdict(list)

    # Analyser les événements
    for event in data['events']:
        minute = event.get('minute', 0)
        events_by_minute[minute].append(event)
        
        player = event.get('player')
        from_opponent = event.get('from_opponent', False)
        event_type = event.get('type', '')
        result_event = event.get('result', '')
        
        if from_opponent:
            # Stats défensives
            if event_type == 'But':
                team_stats['goals_conceded'] += 1
                current_score[1] += 1
            elif event_type == 'Tir cadré':
                team_stats['shots_conceded'] += 1
            elif event_type == 'Tir à côté':
                team_stats['shots_off_conceded'] += 1
                team_stats['shots_conceded'] += 1
        else:
            # Stats offensives et individuelles
            if player and player != 'Adversaire':
                if event_type == 'But':
                    player_stats[player]['goals'] += 1
                    team_stats['goals_scored'] += 1
                    current_score[0] += 1
                elif event_type == 'Tir cadré':
                    player_stats[player]['shots_on_target'] += 1
                    team_stats['shots_total'] += 1
                elif event_type == 'Tir à côté':
                    player_stats[player]['shots_off_target'] += 1
                    team_stats['shots_total'] += 1
                    team_stats['shots_off'] += 1
                elif event_type == 'Passe':
                    player_stats[player]['passes'] += 1
                elif event_type == 'Passe décisive':
                    player_stats[player]['passes'] += 1
                    player_stats[player]['key_passes'] += 1
                elif event_type == 'Tacle':
                    player_stats[player]['tackles'] += 1
                elif event_type == 'Interception':
                    player_stats[player]['interceptions'] += 1
                elif event_type == 'Duel':
                    player_stats[player]['duels'] += 1
                    if result_event == 'won':
                        player_stats[player]['duels_won'] += 1
                elif event_type == 'Fautes subies':
                    player_stats[player]['fouls_suffered'] += 1
                
                # Assists
                if 'assist' in event and event['assist']:
                    receiver = event['assist']
                    player_stats[player]['assists'] += 1
                    player_stats[player]['assists_to'][receiver] += 1
        
        # Évolution du score
        if current_score != [0, 0]:
            score_evolution.append(f"{current_score[0]}-{current_score[1]} ({minute}')")

    # Calculer les métriques
    team_off_eff = (team_stats['goals_scored'] / max(1, team_stats['shots_total'])) * 100
    team_def_eff = (team_stats['goals_conceded'] / max(1, team_stats['shots_conceded'])) * 100

    # Répartition temporelle des buts
    time_ranges = [(0, 9), (10, 19), (20, 29), (30, 39), (40, 49), (50, 59), (60, 90)]
    goals_by_range = defaultdict(int)
    for minute, events in events_by_minute.items():
        for event in events:
            if event.get('type') == 'But' and not event.get('from_opponent', False):
                for start, end in time_ranges:
                    if start <= minute <= end:
                        goals_by_range[f"{start}-{end}"] += 1
                        break

    # Générer le rapport
    report = f"""# Rapport d'analyse : {team_home} VS {team_away}

**Jour de match** : {match_info.get('match_date', 'N/A')}  
**Adversaire** : {team_away}  
**Score** : {result}

## Résumé exécutif

Match {team_home} contre {team_away} terminé sur le score de {result}. Analyse basée sur les événements collectés.

## Métriques Offensives ({team_home})

| Métrique        | Valeur | Analyse      |
| --------------- | ------ | ------------ |
| Buts marqués    | {team_stats['goals_scored']}      | Performance offensive |
| Tirs totaux     | {team_stats['shots_total']}      | Occasions créées |
| Tirs hors cadre | {team_stats['shots_off']}      | Précision à améliorer |
| Efficacité (%)  | {team_off_eff:.1f}%     | Taux de conversion |

## Métriques Défensives ({team_away})

| Métrique       | Valeur | Analyse      |
| -------------- | ------ | ------------ |
| Buts encaissés | {team_stats['goals_conceded']}      | Solidité défensive |
| Tirs subis     | {team_stats['shots_conceded']}      | Pression adverse |
| Efficacité (%) | {team_def_eff:.1f}%     | Efficacité adverse |

## Performances Individuelles

### 🔥 Les Buteurs

| Joueur  | Buts | Tirs | Efficacité |
| ------- | ---- | ---- | ---------- |
"""

    # Buteurs
    goal_scorers = [(p, s['goals'], s['shots_on_target'] + s['shots_off_target']) 
                   for p, s in player_stats.items() if s['goals'] > 0]
    goal_scorers.sort(key=lambda x: x[1], reverse=True)
    for player, goals, shots in goal_scorers:
        eff = (goals / max(1, shots)) * 100
        report += f"| {player} | {goals}    | {shots}    | {eff:.1f}%         |\n"
    if not goal_scorers:
        report += "| Aucun | 0    | 0    | 0.0%         |\n"

    report += "\n### Les passes décisives\n\n| Joueur  | Passes décisives |\n| ------- | ---------------- |\n"
    
    # Passes décisives
    key_passers = [(p, s['key_passes']) for p, s in player_stats.items() if s['key_passes'] > 0]
    key_passers.sort(key=lambda x: x[1], reverse=True)
    for player, key_passes in key_passers:
        report += f"| {player} | {key_passes}                |\n"
    if not key_passers:
        report += "| Aucun | 0                |\n"

    # Réseau de passes par joueur
    report += "\n### Réseau de passes par joueur\n\n"
    for player, stats in sorted(player_stats.items()):
        if stats['assists_to']:
            report += f"**{player}** :\n"
            for receiver, count in sorted(stats['assists_to'].items()):
                report += f"- → {receiver} ({count} assist(s))\n"
            report += "\n"

    # Répartition temporelle
    report += "## Répartition temporelle\n\n| Tranche (min) | Buts marqués |\n| ------------- | ------------ |\n"
    for start, end in time_ranges:
        range_key = f"{start}-{end}"
        goals = goals_by_range[range_key]
        report += f"| {range_key}           | {goals}            |\n"

    # Analyse du Momentum
    report += "\n## Analyse du Momentum\n\n### Évolution du score\n\n"
    if score_evolution:
        report += "0-0 (0') → " + " → ".join(score_evolution) + "\n"
    else:
        report += "0-0 (pas de buts)\n"

    # Fenêtres de scoring (simplifié)
    report += "\n### Fenêtres de scoring\n\n| Équipe | Période | Buts |\n| ------ | ------- | ---- |\n"
    scoring_periods = []
    for range_key, goals in goals_by_range.items():
        if goals > 0:
            scoring_periods.append((team_home, range_key, goals))
    for period in scoring_periods:
        report += f"| {period[0]} | {period[1]}   | {period[2]}    |\n"
    if not scoring_periods:
        report += "| Aucune | -   | 0    |\n"

    # Résilience (simplifié)
    conceded_times = [event['minute'] for event in data['events'] 
                     if event.get('type') == 'But' and event.get('from_opponent', False)]
    reaction_times = []
    for i in range(1, len(conceded_times)):
        reaction_times.append(conceded_times[i] - conceded_times[i-1])
    avg_reaction = sum(reaction_times) / len(reaction_times) if reaction_times else 0

    report += f"\n### Résilience\n\nTemps moyen de réaction après but encaissé : {avg_reaction:.1f} minutes\n"

    # Points forts, améliorations, recommandations (basés sur données)
    report += "\n## Points forts\n\n1. " + (f"{max(player_stats.keys(), key=lambda p: player_stats[p]['goals'])} a marqué {max((s['goals'] for s in player_stats.values()), default=0)} buts" if player_stats else "Aucun but marqué")
    report += "\n2. " + (f"{max(player_stats.keys(), key=lambda p: player_stats[p]['assists'])} a délivré {max((s['assists'] for s in player_stats.values()), default=0)} assists" if player_stats else "Aucune assist")
    report += "\n3. Bonne activité défensive avec interceptions et tacles\n"

    report += "\n## Améliorations possibles\n\n1. Améliorer la précision des tirs\n2. Augmenter le nombre de passes décisives\n3. Réduire les fautes subies\n"

    report += "\n## Recommandations\n\n1. Travailler la finition devant le but\n2. Développer les combinaisons en attaque\n3. Renforcer la concentration défensive\n"

    report += "\n## Conclusion\n\nAnalyse complète du match basée sur les données collectées. Performance globale satisfaisante avec des points d'amélioration identifiés.\n"

    # Section Sources
    report += "\n---\n\n## Sources\n\n- " + json_file + "\n- Données d'événements match parsées\n- Profils joueurs JSON (si fournis)\n"

    # Écrire le rapport
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Rapport généré : {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Simulate performance analysis and generate report")
    parser.add_argument('json_file', help='JSON file with match events')
    parser.add_argument('output_file', help='Output markdown file')
    
    args = parser.parse_args()
    simulate_performance_analysis(args.json_file, args.output_file)

if __name__ == "__main__":
    main()