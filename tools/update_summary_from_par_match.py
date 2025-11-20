import re

MD_PATH = 'completed-tasks/competitions/season_review_2025.md'


def read_md():
    with open(MD_PATH, 'r', encoding='utf-8') as f:
        return f.read()


def write_md(content):
    with open(MD_PATH, 'w', encoding='utf-8') as f:
        f.write(content)


def parse_par_match_table(md):
    header = '## Par match (synthèse)'
    idx = md.find(header)
    if idx == -1:
        raise SystemExit('Par match header not found')
    # find next top-level header after this
    next_idx = md.find('\n## ', idx+1)
    block = md[idx:next_idx] if next_idx != -1 else md[idx:]
    rows = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith('|'):
            continue
        parts = [p.strip() for p in line.split('|')]
        # table rows have at least 5 parts: | Date | Score | Tirs Nous | Tirs Eux |
        if len(parts) < 5:
            continue
        # skip header divider
        if parts[1].lower().startswith('date'):
            continue
        if parts[1].startswith('---'):
            continue
        date = parts[1]
        score = parts[2]
        tirs_nous = parts[3]
        tirs_eux = parts[4]
        try:
            tn = int(re.sub(r'[^0-9]', '', tirs_nous))
        except Exception:
            tn = 0
        try:
            te = int(re.sub(r'[^0-9]', '', tirs_eux))
        except Exception:
            te = 0
        rows.append({'date': date, 'tirs_nous': tn, 'tirs_eux': te})
    return rows


def update_summary(md, total_nous, total_eux, matches):
    # replace the two lines starting with '- Tirs pour:' and '- Tirs contre:' in the Résumé chiffré block
    start = md.find('## Résumé chiffré')
    if start == -1:
        raise SystemExit('Résumé chiffré header not found')
    end = md.find('\n## ', start+1)
    summary = md[start:end] if end != -1 else md[start:]

    avg_nous = (total_nous / matches) if matches > 0 else 0
    avg_eux = (total_eux / matches) if matches > 0 else 0

    new_summary = []
    for line in summary.splitlines():
        if line.strip().startswith('- Tirs pour:'):
            new_summary.append(f'- Tirs pour: **{total_nous}** ({avg_nous:.1f} / match)')
        elif line.strip().startswith('- Tirs contre:'):
            new_summary.append(f'- Tirs contre: **{total_eux}** ({avg_eux:.1f} / match)')
        else:
            new_summary.append(line)

    md2 = md[:start] + '\n'.join(new_summary) + md[end:] if end != -1 else md[:start] + '\n'.join(new_summary)
    return md2


if __name__ == '__main__':
    md = read_md()
    rows = parse_par_match_table(md)
    total_nous = sum(r['tirs_nous'] for r in rows)
    total_eux = sum(r['tirs_eux'] for r in rows)
    matches = len(rows)
    new_md = update_summary(md, total_nous, total_eux, matches)
    write_md(new_md)
    print(f'Updated summary: Tirs pour={total_nous}, Tirs contre={total_eux}, matches={matches}')
