#!/usr/bin/env python3
"""Generate aggregated match metrics from the parsed JSON for a single match.
Reads: .memory-bank/competitions/match_reports/{matchday}/{matchday}.json
Writes:
 - .memory-bank/competitions/match_reports/{matchday}/parsed_by_side.csv
 - .memory-bank/competitions/match_reports/{matchday}/analysis_report.md
 - prints a short summary
"""
import json
import csv
import sys
from pathlib import Path
from collections import defaultdict

MATCHDAY = '2025-09-27'
BASE = Path('.memory-bank/competitions/match_reports') / MATCHDAY
INPUT = BASE / f"{MATCHDAY}.json"
CSV_OUT = BASE / 'parsed_by_side.csv'
REPORT_OUT = BASE / 'analysis_report.md'

if not INPUT.exists():
    print(f"Input JSON not found: {INPUT}")
    sys.exit(1)

with open(INPUT, 'r', encoding='utf-8') as f:
    data = json.load(f)

events = data.get('events', [])
team_name = data.get('team') or data.get('our_team') or 'US'
opp_name = data.get('opponent') or data.get('opponent_team') or 'OPP'

# Normalize event types
for e in events:
    if 'type' in e and isinstance(e['type'], str):
        t = e['type'].lower()
        if t in ('goal', 'but'):
            e['classification'] = 'goal'
        elif t in ('miss', 'tir à côté', 'tir a côté'):
            e['classification'] = 'miss'
        elif t in ('save', 'arrêt', 'tir arrêté'):
            e['classification'] = 'save'
        elif t in ('post', 'poteau', 'transversale'):
            e['classification'] = 'post'
        else:
            e['classification'] = t
    else:
        e['classification'] = e.get('classification') or ''

# Build per-player stats
player = defaultdict(lambda: {'goals':0,'shots':0,'misses':0,'assists':0,'saves':0})
team_goals = 0
opp_goals = 0
team_shots = 0
opp_shots = 0

# Determine which events are for team vs opponent from JSON structure: events with player from our team list are ours.
# The JSON appears to list only team events and saves; we will treat named players as team events and unlabeled goals as team when context suggests.

for e in events:
    cls = e.get('classification')
    player_name = e.get('player')
    minute = e.get('minute')
    detail = e.get('detail') or ''

    # Decide if event is our team or opponent. In this JSON, named players are from USAO U8 (our team)
    is_ours = bool(player_name)

    if cls == 'goal':
        if is_ours:
            player[player_name]['goals'] += 1
            player[player_name]['shots'] += 1
            team_goals += 1
            team_shots += 1
        else:
            # opponent goal
            opp_goals += 1
            opp_shots += 1
    elif cls == 'miss':
        if is_ours:
            player[player_name]['misses'] += 1
            player[player_name]['shots'] += 1
            team_shots += 1
        else:
            opp_shots += 1
    elif cls == 'save':
        # saves could be by our GK (player) or observed saves by opponent GK
        if player_name:
            player[player_name]['saves'] += 1
        # treat as opponent shot on us
        opp_shots += 1
    elif cls in ('post','poteau'):
        # post counts as shot
        if is_ours:
            player[player_name]['shots'] += 1
            player[player_name]['misses'] += 1
            team_shots += 1
        else:
            opp_shots += 1
    else:
        # Other classifications ignored for shot counting
        pass

# Compute efficacy per player
rows = []
for name, stats in sorted(player.items(), key=lambda x: (-x[1]['goals'], x[0])):
    goals = stats['goals']
    shots = stats['shots']
    misses = stats['misses']
    assists = stats.get('assists',0)
    saves = stats.get('saves',0)
    efficacy = (goals / shots * 100) if shots>0 else None
    rows.append({
        'player': name,
        'goals': goals,
        'assists': assists,
        'misses': misses,
        'shots': shots,
        'saves': saves,
        'efficacy_pct': f"{efficacy:.1f}" if efficacy is not None else 'N/A'
    })

# Write CSV
with open(CSV_OUT, 'w', newline='', encoding='utf-8') as cf:
    fieldnames = ['player','goals','assists','misses','shots','saves','efficacy_pct']
    w = csv.DictWriter(cf, fieldnames=fieldnames)
    w.writeheader()
    for r in rows:
        w.writerow(r)

# Build report
from datetime import datetime
p1_goals = sum(1 for e in events if e.get('classification')=='goal' and (e.get('minute') or 0) <= 25)
p2_goals = sum(1 for e in events if e.get('classification')=='goal' and (e.get('minute') or 0) > 25)

team_total_shots = team_shots
opp_total_shots = opp_shots
team_eff = (team_goals / team_total_shots*100) if team_total_shots>0 else 0
opp_eff = (opp_goals / opp_total_shots*100) if opp_total_shots>0 else 0

md = []
md.append(f"# Analyse automatique: {team_name} {team_goals} - {opp_goals} {opp_name}")
md.append(f"*Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
md.append('')
md.append('## Résumé')
md.append(f"- Score: **{team_name} {team_goals} - {opp_goals} {opp_name}**")
md.append(f"- Tirs (estimés): {team_total_shots} (équipe), {opp_total_shots} (adversaire)")
md.append(f"- Efficacité: {team_eff:.1f}% (équipe), {opp_eff:.1f}% (adversaire)")
md.append('')
md.append('## Top joueurs')
for r in rows:
    md.append(f"- **{r['player']}**: {r['goals']} buts, {r['shots']} tirs, efficacité {r['efficacy_pct']}%")
md.append('')
md.append('## Distribution temporelle')
md.append(f"- Période 1 (0-25'): {p1_goals} buts")
md.append(f"- Période 2 (26-...): {p2_goals} buts")
md.append('')
md.append('## Recommandations rapides')
md.append('- Travailler la précision de tir pour les joueurs avec faible efficacité (voir CSV).')
md.append('- Renforcer les sorties défensives sur transitions rapides (quelques saves observées).')
md.append('')
md.append('## Fichiers générés')
md.append(f'- `{CSV_OUT}`')
md.append(f'- `{REPORT_OUT}`')

REPORT_OUT.write_text('\n'.join(md), encoding='utf-8')

print('✅ Analyse terminée')
print(f'  • CSV: {CSV_OUT}')
print(f'  • Rapport: {REPORT_OUT}')
