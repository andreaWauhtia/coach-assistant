import os
import glob
import json
import re
from collections import Counter

MD_PATH = 'completed-tasks/competitions/season_review_2025.md'


def read_md():
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        return f.read()


def write_md(content):
    with open(MD_PATH, 'w', encoding='utf-8') as f:
        f.write(content)


def parse_par_match_dates(md):
    header = '## Par match (synthèse)'
    idx = md.find(header)
    if idx == -1:
        raise SystemExit('Par match header not found')
    next_idx = md.find('\n## ', idx+1)
    block = md[idx:next_idx] if next_idx != -1 else md[idx:]
    dates = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith('|'):
            continue
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 5:
            continue
        if parts[1].lower().startswith('date'):
            continue
        if parts[1].startswith('---'):
            continue
        dates.append(parts[1])
    return dates


def find_json_for_date(date):
    folder = os.path.join('completed-tasks', 'competitions', 'match_reports', date)
    if not os.path.isdir(folder):
        return None
    js = glob.glob(os.path.join(folder, '*.json'))
    if not js:
        return None
    for c in js:
        if date in os.path.basename(c):
            return c
    return js[0]


def collect_players_from_json(jf):
    players = set()
    try:
        with open(jf, 'r', encoding='utf-8') as f:
            j = json.load(f)
        pp = j.get('players_present')
        if isinstance(pp, list) and pp:
            for p in pp:
                if p:
                    players.add(p)
            return players
        # fallback: extract from events
        for e in j.get('events', []):
            p = e.get('player')
            if p:
                players.add(p)
    except Exception:
        pass
    return players


def compute_participation(dates):
    counts = Counter()
    missing = []
    for d in dates:
        jf = find_json_for_date(d)
        if not jf:
            missing.append(d)
            continue
        players = collect_players_from_json(jf)
        if not players:
            missing.append(d)
        for p in players:
            counts[p] += 1
    return counts, missing


def build_table(counts, total_matches):
    lines = []
    lines.append('## Participation des joueurs (saison)')
    lines.append('')
    lines.append(f'Total de matches considérés: **{total_matches}**')
    lines.append('')
    lines.append('| Joueur | Apparitions | % de participation |')
    lines.append('|---|---:|---:|')
    for p, c in counts.most_common():
        pct = (c / total_matches * 100) if total_matches>0 else 0
        lines.append(f'| {p} | {c} | {pct:.1f}% |')
    lines.append('')
    return '\n'.join(lines)


def insert_before_caveats(md, table_md):
    cave_header = '\n## Caveats'
    idx = md.find(cave_header)
    if idx == -1:
        # append at end
        if not md.endswith('\n'):
            md += '\n'
        return md + '\n' + table_md + '\n'
    return md[:idx] + '\n' + table_md + '\n' + md[idx+1:]


if __name__ == '__main__':
    md = read_md()
    dates = parse_par_match_dates(md)
    counts, missing = compute_participation(dates)
    total_matches = len(dates)
    table_md = build_table(counts, total_matches)
    new_md = insert_before_caveats(md, table_md)
    write_md(new_md)
    print(f'Inserted participation table for {len(counts)} players. Missing json for {len(missing)} matches: {missing}')
