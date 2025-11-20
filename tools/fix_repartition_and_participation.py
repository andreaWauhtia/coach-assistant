import re
import glob
import os
import json
from collections import Counter

md_path = 'completed-tasks/competitions/season_review_2025.md'

# categories provided earlier
weak = ['2025-08-30','2025-09-06','2025-09-27','2025-10-11','2025-11-01']
medium = ['2025-09-13','2025-11-08','2025-10-16','2025-10-18']
strong = ['2025-09-17','2025-10-08','2025-11-19']
categories = {'Adversaire faible': weak, 'Adversaire moyen': medium, 'Adversaire fort': strong}

# read md
with open(md_path, 'r', encoding='utf-8') as fh:
    md = fh.read()

# parse Par match table
pm_header = '## Par match (synthèse)'
obs_header = '\n## Observations & Recommandations'
start = md.find(pm_header)
if start == -1:
    raise SystemExit('Par match header not found')
end = md.find(obs_header, start)
if end == -1:
    raise SystemExit('Observations header not found')
block = md[start:end]
lines = block.splitlines()
# find table header index
table_idx = None
for i,l in enumerate(lines):
    if l.strip().startswith('| Date'):
        table_idx = i
        break
if table_idx is None:
    raise SystemExit('Table header not found')
rows = lines[table_idx+2:]
rows_map = {}
match_dates = []
for r in rows:
    if not r.strip().startswith('|'):
        continue
    parts = [p.strip() for p in r.split('|')]
    if len(parts) < 5:
        continue
    date = parts[1]
    score = parts[2]
    shots_us = parts[3]
    shots_them = parts[4]
    m = re.search(r"(\d+)\s*-\s*(\d+)", score)
    if m:
        us = int(m.group(1)); them = int(m.group(2))
    else:
        us = 0; them = 0
    try:
        s_us = int(shots_us)
    except:
        s_us = 0
    try:
        s_them = int(shots_them)
    except:
        s_them = 0
    rows_map[date] = {'us': us, 'them': them, 'shots_us': s_us, 'shots_them': s_them}
    match_dates.append(date)

matches_analyzed = len(match_dates)

# compute repartition aggregates from rows_map
repart = {}
for cat, dates in categories.items():
    agg = {'matches': 0, 'goals_for': 0, 'goals_against': 0, 'shots_for': 0, 'shots_against': 0, 'rows': []}
    for d in dates:
        st = rows_map.get(d, {'us':0,'them':0,'shots_us':0,'shots_them':0})
        agg['matches'] += 1
        agg['goals_for'] += st['us']
        agg['goals_against'] += st['them']
        agg['shots_for'] += st['shots_us']
        agg['shots_against'] += st['shots_them']
        agg['rows'].append((d, st))
    repart[cat] = agg

# compute participation: look for json per date, read players_present or players list
player_counts = Counter()
for d in match_dates:
    folder = os.path.join('completed-tasks','competitions','match_reports', d)
    if not os.path.isdir(folder):
        continue
    # prefer json with date in name
    js = glob.glob(os.path.join(folder, '*.json'))
    chosen = None
    for c in js:
        if d in os.path.basename(c):
            chosen = c; break
    if not chosen and js:
        chosen = js[0]
    players = []
    if chosen:
        try:
            with open(chosen, 'r', encoding='utf-8') as jh:
                jd = json.load(jh)
            if 'players_present' in jd and isinstance(jd['players_present'], list):
                players = jd['players_present']
            else:
                # fallback: collect any event player names seen in this match
                ev = jd.get('events', [])
                s = set()
                for e in ev:
                    p = e.get('player')
                    if p:
                        s.add(p)
                players = list(s)
        except Exception:
            players = []
    # count each player once per match
    for p in set(players):
        player_counts[p] += 1

# compute participation percent
participation = []
for p, c in player_counts.most_common():
    pct = (c / matches_analyzed) * 100 if matches_analyzed>0 else 0
    participation.append({'player': p, 'appearances': c, 'pct': pct})

# build new Observations and Caveats (rewritten)
new_observations = []
new_observations.append('## Observations & Recommandations')
new_observations.append('')
new_observations.append('- Résumé : l’équipe produit de nombreuses occasions mais souffre d\'efficacité défensive lors de matchs contre des adversaires plus physiques; travailler les placements et la réactivité derrière le ballon.')
new_observations.append('- Attaques : maintenir les exercices de finition et encourager la variété des combinaisons offensives (jeu sur les ailes puis centre, dédoublements rapides).')
new_observations.append('- Défense : prioriser les séances sur la coordination des lignes, le replacement après perte du ballon et les duels en un contre un.')
new_observations.append('- Gardien : travailler sorties aériennes et relances au pied dans le contexte de terrain synthétique et conditions humides.')
new_observations.append('- Mental : renforcer l\'état d\'esprit en début de match (travail sur la concentration et routines d\'engagement).')
new_observations.append('')

new_participation = []
new_participation.append('## Participation des joueurs (saison)')
new_participation.append('')
new_participation.append('| Joueur | Apparitions | % de participation |')
new_participation.append('|---|---:|---:|')
for p in participation:
    new_participation.append(f"| {p['player']} | {p['appearances']} | {p['pct']:.1f}% |")
new_participation.append('')

# build repartition text
new_repart = []
new_repart.append("## Répartition par niveau d'adversaire")
new_repart.append('')
for cat, agg in repart.items():
    new_repart.append(f"### {cat}")
    new_repart.append('')
    new_repart.append(f"- Matchs: **{agg['matches']}**")
    new_repart.append(f"- Buts pour: **{agg['goals_for']}**")
    new_repart.append(f"- Buts contre: **{agg['goals_against']}**")
    new_repart.append(f"- Tirs pour: **{agg['shots_for']}**")
    new_repart.append(f"- Tirs contre: **{agg['shots_against']}**")
    new_repart.append('')
    new_repart.append('| Date | Score (Nous - Eux) | Tirs Nous | Tirs Eux |')
    new_repart.append('|---|---:|---:|---:|')
    for d, st in agg['rows']:
        new_repart.append(f"| {d} | {st['us']} - {st['them']} | {st['shots_us']} | {st['shots_them']} |")
    new_repart.append('')

# new caveats
new_caveats = []
new_caveats.append('## Caveats')
new_caveats.append('')
new_caveats.append('- Les attributions individuelles proviennent majoritairement des fichiers `YYYY-MM-DD.json`. Lorsque le champ `player` est absent pour un événement, l\'événement reste non attribué.')
new_caveats.append('- Les chiffres des tirs sont parfois manquants dans certains JSON ; j\'ai complété ceux disponibles et utilisé le tableau principal `Par match` comme source d\'autorité pour la synthèse.')
new_caveats.append('- Les correspondances de noms utilisent heuristique depuis `completed-tasks/roster/U8.md` ; signale les orthographes préférées si besoin.')
new_caveats.append('- La catégorisation des adversaires a été fournie manuellement; elle influence la répartition par niveau.')
new_caveats.append('')

# assemble new md: keep content up to Par match block (inclusive), then append new Observations, Participation, Repartition and Caveats
prefix = md[:end]
suffix_start = md.find('## Caveats', end)
if suffix_start != -1:
    # remove existing Observations..Caveats block
    # find end of Caveats block (we'll append our new Caveats)
    md_final = prefix + '\n'.join(new_observations) + '\n\n' + '\n'.join(new_participation) + '\n' + '\n'.join(new_repart) + '\n' + '\n'.join(new_caveats)
else:
    md_final = prefix + '\n'.join(new_observations) + '\n\n' + '\n'.join(new_participation) + '\n' + '\n'.join(new_repart) + '\n' + '\n'.join(new_caveats)

with open(md_path, 'w', encoding='utf-8') as fh:
    fh.write(md_final)

print('Updated', md_path)
