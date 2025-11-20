import re

md_path = 'completed-tasks/competitions/season_review_2025.md'
date_to_fix = '2025-11-19'
opponent_shots = 25

# categories same as before
weak = ['2025-08-30','2025-09-06','2025-09-27','2025-10-11','2025-11-01']
medium = ['2025-09-13','2025-11-08','2025-10-16','2025-10-18']
strong = ['2025-09-17','2025-10-08','2025-11-19']
categories = {'Adversaire faible': weak, 'Adversaire moyen': medium, 'Adversaire fort': strong}

with open(md_path, 'r', encoding='utf-8') as fh:
    md = fh.read()

# find Par match table
pm_header = '## Par match (synthèse)'
start = md.find(pm_header)
if start == -1:
    raise SystemExit('Par match header not found')
end = md.find('\n## Observations', start)
if end == -1:
    end = len(md)
block = md[start:end]
lines = block.splitlines()
# locate table header
table_start = None
for i,l in enumerate(lines):
    if l.strip().startswith('| Date'):
        table_start = i
        break
if table_start is None:
    raise SystemExit('Table header not found')
# rows start at table_start+2
rows = lines[table_start+2:]
new_rows = []
for r in rows:
    if not r.strip().startswith('|'):
        new_rows.append(r)
        continue
    parts = [p for p in r.split('|')]
    # parts: ['', ' Date ', ' Score (Nous - Eux) ', ' Tirs Nous ', ' Tirs Eux ', '']
    if len(parts) < 6:
        new_rows.append(r)
        continue
    date = parts[1].strip()
    if date == date_to_fix:
        # set opponent shots
        parts[4] = ' {} '.format(opponent_shots)
        new_r = '|'.join(parts)
        new_rows.append(new_r)
    else:
        new_rows.append(r)

# rebuild block
new_block_lines = lines[:table_start+2] + new_rows
new_block = '\n'.join(new_block_lines)
md_updated = md[:start] + new_block + md[end:]

# rebuild repartition from Par match table
# parse rows into map
rows_map = {}
for r in new_rows:
    if not r.strip().startswith('|'):
        continue
    parts = [p.strip() for p in r.split('|')]
    if len(parts) < 6:
        continue
    d = parts[1]
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
    rows_map[d] = {'us': us, 'them': them, 'shots_us': s_us, 'shots_them': s_them}

# build repartition text
out_lines = []
out_lines.append('\n## Répartition par niveau d\'adversaire\n')
for cat, dates in categories.items():
    agg_matches = 0
    agg_gf = 0
    agg_ga = 0
    agg_sf = 0
    agg_sa = 0
    rows_list = []
    for d in dates:
        st = rows_map.get(d, {'us':0,'them':0,'shots_us':0,'shots_them':0})
        agg_matches += 1
        agg_gf += st['us']
        agg_ga += st['them']
        agg_sf += st['shots_us']
        agg_sa += st['shots_them']
        rows_list.append((d, st))
    out_lines.append(f"### {cat}\n")
    out_lines.append(f"- Matchs: **{agg_matches}**")
    out_lines.append(f"- Buts pour: **{agg_gf}**")
    out_lines.append(f"- Buts contre: **{agg_ga}**")
    out_lines.append(f"- Tirs pour: **{agg_sf}**")
    out_lines.append(f"- Tirs contre: **{agg_sa}**\n")
    out_lines.append('| Date | Score (Nous - Eux) | Tirs Nous | Tirs Eux |')
    out_lines.append('|---|---:|---:|---:|')
    for d, st in rows_list:
        out_lines.append(f"| {d} | {st['us']} - {st['them']} | {st['shots_us']} | {st['shots_them']} |")
    out_lines.append('\n')

# replace existing repartition section
rep_header = '\n## Répartition par niveau d\'adversaire'
rep_idx = md_updated.find(rep_header)
if rep_idx != -1:
    md_final = md_updated[:rep_idx] + '\n'.join(out_lines)
else:
    md_final = md_updated + '\n'.join(out_lines)

with open(md_path, 'w', encoding='utf-8') as fh:
    fh.write(md_final)

print('Applied fix and updated repartition in', md_path)
