import re
from collections import Counter

MD_PATH = 'completed-tasks/competitions/season_review_2025.md'


def read_md():
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        return f.read()


def write_md(s):
    with open(MD_PATH, 'w', encoding='utf-8') as f:
        f.write(s)


def extract_participation_block(md):
    start_marker = '## Participation des joueurs (saison)'
    start = md.find(start_marker)
    if start == -1:
        return None, None, None
    # find next header after start
    next_h = md.find('\n## ', start+1)
    block = md[start: next_h] if next_h != -1 else md[start:]
    return start, next_h, block


def parse_table(block):
    lines = block.splitlines()
    rows = []
    for l in lines:
        if l.strip().startswith('|') and not l.strip().startswith('|---') and 'Joueur' not in l:
            parts = [p.strip() for p in l.split('|')]
            if len(parts) >= 4:
                name = parts[1]
                try:
                    app = int(parts[2])
                except Exception:
                    app = 0
                rows.append((name, app))
    return rows


def build_canonical_map(names):
    # prefer longest name; map any shorter name that is substring to the longest containing it
    canon = {}
    sorted_names = sorted(names, key=lambda s: -len(s))
    for i, longname in enumerate(sorted_names):
        for short in sorted_names[i+1:]:
            if short and short != longname and short in longname:
                canon[short] = longname
    return canon


def collapse_rows(rows, canon_map):
    collapsed = Counter()
    for name, app in rows:
        key = name
        if name in canon_map:
            key = canon_map[name]
        collapsed[key] += app
    return collapsed


def build_table_md(collapsed, total_matches):
    lines = []
    lines.append('## Participation des joueurs (saison)')
    lines.append('')
    lines.append(f'Total de matches considérés: **{total_matches}**')
    lines.append('')
    lines.append('| Joueur | Apparitions | % de participation |')
    lines.append('|---|---:|---:|')
    for p, c in collapsed.most_common():
        pct = (c / total_matches * 100) if total_matches>0 else 0
        lines.append(f'| {p} | {c} | {pct:.1f}% |')
    lines.append('')
    return '\n'.join(lines)


if __name__ == '__main__':
    md = read_md()
    start, next_h, block = extract_participation_block(md)
    if block is None:
        print('Participation block not found')
        raise SystemExit(1)
    rows = parse_table(block)
    names = [r[0] for r in rows]
    canon = build_canonical_map(names)
    collapsed = collapse_rows(rows, canon)
    # try to infer total matches from existing text
    m = re.search(r'Total de matches considérés: \*\*(\d+)\*\*', block)
    total = int(m.group(1)) if m else 0
    new_block = build_table_md(collapsed, total)
    # replace old block
    new_md = md[:start] + new_block + (md[next_h:] if next_h else '')
    write_md(new_md)
    print('Normalized participation table; merged names:', len(canon), 'mappings')
