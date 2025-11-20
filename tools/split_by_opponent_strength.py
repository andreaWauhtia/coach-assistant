import glob
import os
import json
import re


def extract_date_from_filename(fname):
    m = re.search(r'(\d{4}-\d{2}-\d{2})', fname)
    if m:
        return m.group(1)
    m = re.search(r'(\d{8})', fname)
    if m:
        s = m.group(1)
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    return None


# user-provided categorizations
weak = ['2025-08-30','2025-09-06','2025-09-27','2025-10-11','2025-11-01']
medium = ['2025-09-13','2025-11-08','2025-10-16','2025-10-18']
strong = ['2025-09-17','2025-10-08','2025-11-19']

categories = {
    'Adversaire faible': weak,
    'Adversaire moyen': medium,
    'Adversaire fort': strong,
}

# helper: find match JSON or MD for a date
def find_match_files_for_date(date):
    base = 'completed-tasks/competitions/match_reports'
    result = {'json': None, 'md': None}
    # look for folder matching date
    candidate_dir = os.path.join(base, date)
    if os.path.isdir(candidate_dir):
        # find json
        js = glob.glob(os.path.join(candidate_dir, '*.json'))
        if js:
            # prefer file containing the date
            chosen = None
            for c in js:
                if date in os.path.basename(c):
                    chosen = c
                    break
            if not chosen:
                for c in js:
                    if os.path.basename(c).lower().startswith('match_'):
                        chosen = c
                        break
            if not chosen:
                chosen = js[0]
            result['json'] = chosen
        # find md
        md = glob.glob(os.path.join(candidate_dir, '*.md'))
        if md:
            # prefer date-named md
            chosen_md = None
            for m in md:
                if date in os.path.basename(m):
                    chosen_md = m
                    break
            if not chosen_md:
                chosen_md = md[0]
            result['md'] = chosen_md
    return result


# extract uf/of and shots from json or md
def extract_match_stats(date):
    files = find_match_files_for_date(date)
    # defaults
    uf = None
    of = None
    shots_for = None
    shots_against = None
    # try json
    jf = files.get('json')
    if jf:
        try:
            with open(jf, 'r', encoding='utf-8') as fh:
                j = json.load(fh)
            # try score1/score2
            if 'score1' in j and 'score2' in j:
                s1 = j.get('score1')
                s2 = j.get('score2')
                t1 = (j.get('team1') or '').lower()
                t2 = (j.get('team2') or '').lower()
                our = (j.get('our_team') or '').lower()
                if our and our in t1:
                    uf, of = int(s1), int(s2)
                elif our and our in t2:
                    uf, of = int(s2), int(s1)
                else:
                    # fallback: if team2 looks like USAO take s2
                    if 'usao' in t1:
                        uf, of = int(s1), int(s2)
                    else:
                        uf, of = int(s2), int(s1)
            elif 'score' in j and isinstance(j['score'], dict):
                score_blob = j['score']
                # try pick our key
                our = (j.get('our_team') or '').lower()
                picked = None
                for k,v in score_blob.items():
                    if our and our in str(k).lower():
                        uf = int(v)
                        picked = int(v)
                        break
                if picked is None:
                    for k,v in score_blob.items():
                        if 'usao' in str(k).lower():
                            uf = int(v)
                            picked = int(v)
                            break
                # other value as opponent
                for k,v in score_blob.items():
                    if picked is None or int(v) != picked:
                        if uf is None:
                            uf = int(v)
                        else:
                            of = int(v)
                # if still None attempt nothing
            # shots
            if isinstance(j.get('shots'), dict):
                sb = j['shots']
                on = sb.get('on_target') or sb.get('on') or 0
                off = sb.get('off_target') or sb.get('off') or 0
                shots_for = int(on) + int(off)
        except Exception:
            jf = None
    # fallback to md header
    if (uf is None or of is None) and files.get('md'):
        try:
            with open(files['md'], 'r', encoding='utf-8') as fh:
                text = fh.read()
            us_g = None
            us_tirs = None
            opp_g = None
            opp_tirs = None
            for line in text.splitlines():
                m = re.match(r"- \*\*(.+?)\*\*:\s*(\d+)\s*buts?,\s*(\d+)\s*tirs?", line, re.IGNORECASE)
                if m:
                    team = m.group(1).strip()
                    g = int(m.group(2))
                    s = int(m.group(3))
                    tn = team.lower()
                    if 'usao' in tn or tn.startswith('usao'):
                        us_g = g
                        us_tirs = s
                    else:
                        opp_g = g
                        opp_tirs = s
            if us_g is not None:
                uf = us_g
            if opp_g is not None:
                of = opp_g
            if us_tirs is not None:
                shots_for = (uf or 0) + us_tirs
            if opp_tirs is not None:
                shots_against = (of or 0) + opp_tirs
        except Exception:
            pass
    # final fallbacks
    if uf is None:
        uf = 0
    if of is None:
        of = 0
    if shots_for is None:
        shots_for = 0
    if shots_against is None:
        shots_against = 0
    return {'date': date, 'us': uf, 'them': of, 'shots_for': shots_for, 'shots_against': shots_against}


def aggregate_for_dates(dates):
    agg = {'matches': 0, 'goals_for': 0, 'goals_against': 0, 'shots_for': 0, 'shots_against': 0, 'rows': []}
    for d in dates:
        st = extract_match_stats(d)
        agg['matches'] += 1
        agg['goals_for'] += st['us']
        agg['goals_against'] += st['them']
        agg['shots_for'] += st['shots_for']
        agg['shots_against'] += st['shots_against']
        agg['rows'].append(st)
    return agg


# build output markdown
out_lines = []
out_lines.append('## Répartition par niveau d\'adversaire')
out_lines.append('')
for cat, dates in categories.items():
    agg = aggregate_for_dates(dates)
    out_lines.append(f"### {cat}")
    out_lines.append('')
    out_lines.append(f"- Matchs: **{agg['matches']}**")
    out_lines.append(f"- Buts pour: **{agg['goals_for']}**")
    out_lines.append(f"- Buts contre: **{agg['goals_against']}**")
    out_lines.append(f"- Tirs pour: **{agg['shots_for']}**")
    out_lines.append(f"- Tirs contre: **{agg['shots_against']}**")
    out_lines.append('')
    out_lines.append('| Date | Score (Nous - Eux) | Tirs Nous | Tirs Eux |')
    out_lines.append('|---|---:|---:|---:|')
    for r in agg['rows']:
        out_lines.append(f"| {r['date']} | {r['us']} - {r['them']} | {r['shots_for']} | {r['shots_against']} |")
    out_lines.append('')

import re


def replace_section_in_file(path, header, new_block):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            md = f.read()
    except Exception as e:
        print('Failed to read', path, e)
        return False

    pattern = re.compile(r'(?s)' + re.escape(header) + r'.*?(?=\n## |\Z)')
    new_text = '\n'.join(new_block)
    # remove ALL existing matching sections
    md_clean = pattern.sub('', md)
    # append new section once at end of the document
    if not md_clean.endswith('\n'):
        md_clean += '\n'
    md2 = md_clean + '\n' + new_text + '\n'

    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(md2)
        print('Updated', path)
        return True
    except Exception as e:
        print('Failed to write', path, e)
        return False


# write or replace the section
sr_path = 'completed-tasks/competitions/season_review_2025.md'
header = "## Répartition par niveau d'adversaire"
replace_section_in_file(sr_path, header, out_lines)

print('Done')
