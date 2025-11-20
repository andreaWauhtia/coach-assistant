import re
import glob
import json
import os

md_path = 'completed-tasks/competitions/season_review_2025.md'
excluded = '2025-11-19'

# same categories as before
weak = ['2025-08-30','2025-09-06','2025-09-27','2025-10-11','2025-11-01']
medium = ['2025-09-13','2025-11-08','2025-10-16','2025-10-18']
strong = ['2025-09-17','2025-10-08','2025-11-19']
categories = {'Adversaire faible': weak, 'Adversaire moyen': medium, 'Adversaire fort': strong}

with open(md_path, 'r', encoding='utf-8') as fh:
    md = fh.read()

# find Par match block
pm_header = '## Par match (synthèse)'
obs_header = '\n## Observations'
start = md.find(pm_header)
if start == -1:
    print('Par match header not found')
    raise SystemExit(1)
end = md.find('\n## Observations', start)
if end == -1:
    # fallback to end of file
    end = len(md)
block = md[start:end]
lines = block.splitlines()
# find table header start index
table_start_idx = None
for i,l in enumerate(lines):
    if l.strip().startswith('| Date'):
        table_start_idx = i
        break
if table_start_idx is None:
    print('Table header not found')
    raise SystemExit(1)
# rows start at table_start_idx+2
rows = lines[table_start_idx+2:]
new_rows = []
# helper to find json for date

def find_json_for_date(date):
    folder = os.path.join('completed-tasks','competitions','match_reports', date)
    if not os.path.isdir(folder):
        return None
    js = glob.glob(os.path.join(folder, '*.json'))
    if not js:
        return None
    # prefer file with date in name
    for c in js:
        if date in os.path.basename(c):
            return c
    for c in js:
        if os.path.basename(c).lower().startswith('match_'):
            return c
    return js[0]

updated_rows = []
for r in rows:
    if not r.strip().startswith('|'):
        continue
    parts = [p.strip() for p in r.split('|')]
    # parts: ['', ' Date ', ' Score (Nous - Eux) ', ' Tirs Nous ', ' Tirs Eux ', '']
    if len(parts) < 5:
        updated_rows.append(r)
        continue
    date = parts[1]
    current_shots = parts[3]
    # if excluded date, keep current
    if date == excluded:
        updated_rows.append(r)
        continue
    jf = find_json_for_date(date)
    if jf:
        try:
            with open(jf, 'r', encoding='utf-8') as jh:
                j = json.load(jh)
            if isinstance(j.get('shots'), dict):
                sb = j['shots']
                on = sb.get('on_target') or sb.get('on') or 0
                off = sb.get('off_target') or sb.get('off') or 0
                shots_for = int(on) + int(off)
                # replace parts[3]
                parts[3] = f' {shots_for} '
                new_r = '|'.join(parts)
                updated_rows.append(new_r)
                continue
        except Exception:
            pass
    # no update
    updated_rows.append(r)

# rebuild block
new_block_lines = lines[:table_start_idx+2] + updated_rows
new_block = '\n'.join(new_block_lines)
# replace in md
md_updated = md[:start] + new_block + md[end:]

# Now regenerate the Répartition section entirely using the updated table values
# parse table rows to build a mapping date->stats
rows_map = {}
for r in updated_rows:
    if not r.strip().startswith('|'):
        continue
    parts = [p.strip() for p in r.split('|')]
    if len(parts) < 5:
        continue
    date = parts[1]
    score = parts[2]
    shots_us = parts[3]
    shots_them = parts[4]
    # parse score like '12 - 1'
    m = re.search(r"(\d+)\s*-\s*(\d+)", score)
    if m:
        us = int(m.group(1))
        them = int(m.group(2))
    else:
        us = 0
        them = 0
    try:
        s_us = int(shots_us)
    except Exception:
        s_us = 0
    try:
        s_them = int(shots_them)
    except Exception:
        s_them = 0
    rows_map[date] = {'us': us, 'them': them, 'shots_us': s_us, 'shots_them': s_them}

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

# remove existing repartition section if present
rep_header = '\n## Répartition par niveau d\'adversaire'
rep_idx = md_updated.find(rep_header)
if rep_idx != -1:
    md_final = md_updated[:rep_idx] + '\n'.join(out_lines)
else:
    md_final = md_updated + '\n'.join(out_lines)

with open(md_path, 'w', encoding='utf-8') as fh:
    fh.write(md_final)

print('Updated shots in', md_path)
