import re
import os
import glob
import json
from collections import Counter

MD_PATH = 'completed-tasks/competitions/season_review_2025.md'

def read_md():
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def write_md(content):
    with open(MD_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

def parse_par_match(md):
    header = '## Par match (synthèse)'
    idx = md.find(header)
    if idx == -1:
        raise SystemExit('Par match header not found')
    # find next top-level header after this
    next_idx = md.find('\n## ', idx+1)
    if next_idx == -1:
        block = md[idx:]
    else:
        block = md[idx:next_idx]
    lines = block.splitlines()
    # find table header
    tbl_idx = None
    for i,l in enumerate(lines):
        if l.strip().startswith('| Date'):
            tbl_idx = i
            break
    if tbl_idx is None:
        raise SystemExit('Table header not found')
    rows = []
    for l in lines[tbl_idx+2:]:
        if not l.strip().startswith('|'):
            break
        parts = [p.strip() for p in l.split('|')]
        if len(parts) < 5:
            continue
        date = parts[1]
        score = parts[2]
        shots_us = parts[3]
        shots_them = parts[4]
        m = re.search(r"(\d+)\s*-\s*(\d+)", score)
        us = int(m.group(1)) if m else 0
        them = int(m.group(2)) if m else 0
        try:
            s_us = int(shots_us)
        except:
            s_us = 0
        try:
            s_them = int(shots_them)
        except:
            s_them = 0
        rows.append({'date': date, 'us': us, 'them': them, 'shots_us': s_us, 'shots_them': s_them})
    return idx, (next_idx if next_idx!=-1 else None), rows

def find_json_for_date(date):
    folder = os.path.join('completed-tasks','competitions','match_reports', date)
    if not os.path.isdir(folder):
        return None
    js = glob.glob(os.path.join(folder, '*.json'))
    if not js:
        return None
    for c in js:
        if date in os.path.basename(c):
            return c
    for c in js:
        if os.path.basename(c).lower().startswith('match_'):
            return c
    return js[0]

def compute_participation(dates):
    player_counts = Counter()
    for d in dates:
        jf = find_json_for_date(d)
        players = []
        if jf:
            try:
                with open(jf, 'r', encoding='utf-8') as f:
                    j = json.load(f)
                if isinstance(j.get('players_present'), list):
                    players = j['players_present']
                else:
                    s = set()
                    for e in j.get('events', []):
                        p = e.get('player')
                        if p:
                            s.add(p)
                    players = list(s)
            except Exception:
                players = []
        for p in set(players):
            player_counts[p] += 1
    return player_counts

def build_sections(rows, player_counts):
    # categories as provided earlier
    weak = ['2025-08-30','2025-09-06','2025-09-27','2025-10-11','2025-11-01']
    medium = ['2025-09-13','2025-11-08','2025-10-16','2025-10-18']
    strong = ['2025-09-17','2025-10-08','2025-11-19']
    categories = [('Adversaire faible', weak), ('Adversaire moyen', medium), ('Adversaire fort', strong)]

    # Observations (rewritten)
    obs = []
    obs.append('## Observations & Recommandations')
    obs.append('')
    obs.append('- Bilan général : l\'équipe crée beaucoup d\'occasions (moyenne de tirs élevée) mais souffre parfois défensivement face aux équipes plus physiques. Objectif : consolider le placement défensif et la communication.')
    obs.append('- Offensif : poursuivre le travail sur la finition, varier les combinaisons et favoriser la présence aux abords du but.')
    obs.append('- Défensif : exercices sur la transition défensive, replacement rapide et travail des duels; insistez aussi sur la relance propre du gardien.')
    obs.append('- Mental & Routine : instaurer une routine d\'engagement avant match pour combattre les phases d\'entrée de match défaillantes.')
    obs.append('')

    # Participation
    total_matches = len(rows)
    part = []
    part.append('## Participation des joueurs (saison)')
    part.append('')
    part.append('| Joueur | Apparitions | % de participation |')
    part.append('|---|---:|---:|')
    for p, c in player_counts.most_common():
        pct = (c / total_matches * 100) if total_matches>0 else 0
        part.append(f'| {p} | {c} | {pct:.1f}% |')
    part.append('')

    # Repartition
    repart = []
    repart.append("## Répartition par niveau d'adversaire")
    repart.append('')
    # build a map date->row for reliable lookup (strip dates)
    row_map = {r['date'].strip(): r for r in rows}
    for cat, dates in categories:
        agg_matches = 0
        agg_gf = 0
        agg_ga = 0
        agg_sf = 0
        agg_sa = 0
        repart.append(f'### {cat}')
        repart.append('')
        rows_list = []
        for d in dates:
            key = d.strip()
            row = row_map.get(key)
            if not row:
                row = {'date': d, 'us': 0, 'them': 0, 'shots_us': 0, 'shots_them': 0}
            agg_matches += 1
            agg_gf += row.get('us', 0)
            agg_ga += row.get('them', 0)
            agg_sf += row.get('shots_us', 0)
            agg_sa += row.get('shots_them', 0)
            rows_list.append(row)
        repart.append(f"- Matchs: **{agg_matches}**")
        repart.append(f"- Buts pour: **{agg_gf}**")
        repart.append(f"- Buts contre: **{agg_ga}**")
        repart.append(f"- Tirs pour: **{agg_sf}**")
        repart.append(f"- Tirs contre: **{agg_sa}**")
        repart.append('')
        repart.append('| Date | Score (Nous - Eux) | Tirs Nous | Tirs Eux |')
        repart.append('|---|---:|---:|---:|')
        for r in rows_list:
            repart.append(f"| {r['date']} | {r['us']} - {r['them']} | {r.get('shots_us',0)} | {r.get('shots_them',0)} |")
        repart.append('')

    # Caveats
    cave = []
    cave.append('## Caveats')
    cave.append('')
    cave.append('- Les attributions individuelles proviennent majoritairement des fichiers `YYYY-MM-DD.json`. Si `player` est null dans un événement, l\'événement reste non attribué.')
    cave.append('- Les chiffres des tirs proviennent soit du champ `shots` dans les JSON soit du tableau "Par match"; certaines sources restent incomplètes.')
    cave.append('- Les correspondances de noms utilisent le roster local; signale les orthographes préférées pour améliorer les attributions.')
    cave.append('- La catégorisation des adversaires a été fournie manuellement et sert uniquement à regrouper les performances par niveau.')
    cave.append('')

    return '\n'.join(obs), '\n'.join(part), '\n'.join(repart), '\n'.join(cave)

if __name__ == '__main__':
    md = read_md()
    par_idx_start, par_idx_end, rows = parse_par_match(md)
    # prefix: everything up to end of Par match block
    if par_idx_end:
        prefix = md[:par_idx_end]
    else:
        # find end of table by searching for next '## '
        m = re.search(r'\n## ', md[par_idx_start+1:])
        prefix = md[:par_idx_start] + md[par_idx_start:]
    # compute participation based on rows dates
    dates = [r['date'] for r in rows]
    player_counts = compute_participation(dates)
    obs_s, part_s, repart_s, cave_s = build_sections(rows, player_counts)
    new_md = prefix + '\n\n' + obs_s + '\n\n' + part_s + '\n\n' + repart_s + '\n\n' + cave_s
    write_md(new_md)
    print('Rebuilt season review with updated sections.')
