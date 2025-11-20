import json
import glob
import re
import os
from collections import Counter


def load_roster(path):
    names = []
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            text = fh.read()
        # find bolded names like **Name**
        bolds = re.findall(r"\*\*(.+?)\*\*", text)
        for b in bolds:
            # strip role info after parentheses, comma or dash
            name = re.split(r'[(),-]', b)[0].strip()
            if name:
                names.append(name)
    except FileNotFoundError:
        pass
    # deduplicate
    return list(dict.fromkeys(names))


def extract_date_from_filename(fname):
    # try yyyy-mm-dd
    m = re.search(r'(\d{4}-\d{2}-\d{2})', fname)
    if m:
        return m.group(1)
    m = re.search(r'(\d{8})', fname)
    if m:
        s = m.group(1)
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    return None


def match_player_to_roster(player_str, roster):
    if not player_str:
        return None
    p = player_str.lower()
    # exact match
    for r in roster:
        if p == r.lower():
            return r
    # partial match on tokens (first name or last name)
    for r in roster:
        tokens = r.lower().split()
        for t in tokens:
            if t and t in p:
                return r
    return None


files = glob.glob('completed-tasks/competitions/match_reports/**/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md', recursive=True)

roster = load_roster('completed-tasks/roster/U8.md')

# build a set of all raw names seen in MDs to derive canonical forms
all_raw_names = set()
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as fh:
            text = fh.read()
        # find occurrences like '— Name Surname [' or '— Name ['
        names = re.findall(r"—\s*([A-Z][a-zA-Z'\-]+(?:\s+[A-Z][a-zA-Z'\-]+)*)\s*\[", text)
        for n in names:
            all_raw_names.add(n.strip())
    except Exception:
        pass

# build canonical mapping: prefer longest matching name for given token
canonical_map = {}
for raw in sorted(all_raw_names, key=lambda s: -len(s)):
    tokens = raw.split()
    for shorter in list(all_raw_names):
        if shorter == raw:
            continue
        # if shorter is contained as token sequence in raw, map shorter -> raw
        if shorter in raw and len(shorter) < len(raw):
            canonical_map[shorter] = raw


seen_dates = set()
summary = {
    'matches': 0,
    'wins': 0,
    'draws': 0,
    'losses': 0,
    'goals_for': 0,
    'goals_against': 0,
    'shots_for': 0,
    'shots_against': 0,
}
player_goals = Counter()
player_shots = Counter()
per_match = []
for f in sorted(files):
    date = extract_date_from_filename(f)
    if date and date in seen_dates:
        continue
    if date:
        seen_dates.add(date)
    with open(f, 'r', encoding='utf-8') as fh:
        text = fh.read()
    summary['matches'] += 1

    # parse header lines like: - **USAO U8**: 7 buts, 4 tirs hors buts
    us_goals = None
    us_tirs_hors_buts = None
    opp_goals = None
    opp_tirs_hors_buts = None
    for line in text.splitlines():
        m = re.match(r"- \*\*(.+?)\*\*:\s*(\d+)\s*buts?,\s*(\d+)\s*tirs?", line, re.IGNORECASE)
        if m:
            team = m.group(1).strip()
            g = int(m.group(2))
            s = int(m.group(3))
            # identify our team by common token 'usao' or 'usao u8' or 'usaou8' or exactly 'usaou8' or startswith 'USAO'
            tn = team.lower()
            if 'usao' in tn or tn.startswith('usao') or 'usao u8' in tn or 'usao u8' in tn.replace(' ', '') or 'usaou8' in tn:
                us_goals = g
                us_tirs_hors_buts = s
            else:
                opp_goals = g
                opp_tirs_hors_buts = s

    # Hybrid parsing: prefer per-player events from a nearby JSON `match_*.json` file.
    match_player_goals = Counter()
    match_player_shots = Counter()
    us_count = 0
    opp_count = 0
    shots_for = 0
    shots_against = 0

    md_dir = os.path.dirname(f)
    json_candidates = glob.glob(os.path.join(md_dir, '*.json'))
    jf = None
    if json_candidates:
        # prefer a file containing the date in its name
        if date:
            for candidate in json_candidates:
                if date in os.path.basename(candidate):
                    jf = candidate
                    break
        # else prefer files starting with 'match_'
        if not jf:
            for candidate in json_candidates:
                if os.path.basename(candidate).lower().startswith('match_'):
                    jf = candidate
                    break
        # fallback to the first json
        if not jf:
            jf = json_candidates[0]
    if jf:
        try:
            with open(jf, 'r', encoding='utf-8') as jh:
                jdata = json.load(jh)
            seen_events = set()
            # determine whether the JSON's notion of 'us' corresponds to USAO
            json_our_team = (jdata.get('our_team') or jdata.get('team2') or jdata.get('team1') or jdata.get('match_header') or '').lower()
            json_our_is_usao = 'usao' in json_our_team or 'usao u8' in json_our_team or 'usaou8' in json_our_team or 'usao u8' in json_our_team.replace(' ', '')
            for e in jdata.get('events', []):
                minute = e.get('minute') or e.get('min') or e.get('time') or None
                try:
                    minute = int(minute) if minute is not None else None
                except Exception:
                    minute = None
                etype = (e.get('type') or '').strip()
                player_field = e.get('player') or ''
                side = (e.get('side') or '').strip().lower()
                team_field = (e.get('team') or '').strip().lower()

                raw_name = str(player_field).strip()
                matched = match_player_to_roster(raw_name, roster) if raw_name else None
                if not matched and raw_name in canonical_map:
                    player_key = canonical_map[raw_name]
                else:
                    player_key = matched or raw_name

                key = (minute, player_key, (etype or '').lower())
                if key in seen_events:
                    continue
                seen_events.add(key)

                is_goal = 'but' in (etype or '').lower()
                is_shot = any(k in (etype or '').lower() for k in ['tir', 'poteau', 'but', 'arrêt'])

                if is_goal:
                    # prefer explicit team flag from JSON; but map JSON-local 'us' to actual USAO using json_our_is_usao
                    if team_field:
                        if team_field.startswith('us'):
                            is_event_ours = json_our_is_usao
                        elif team_field.startswith('opp'):
                            is_event_ours = not json_our_is_usao
                        else:
                            is_event_ours = json_our_is_usao
                        if is_event_ours:
                            us_count += 1
                            if player_key:
                                match_player_goals[player_key] += 1
                        else:
                            opp_count += 1
                    else:
                        # fallback to side logic
                        if side.startswith('us') or side == 'us' or not side:
                            us_count += 1
                            if player_key:
                                match_player_goals[player_key] += 1
                        else:
                            opp_count += 1
                if is_shot:
                    if team_field:
                        if team_field.startswith('us'):
                            is_event_ours = json_our_is_usao
                        elif team_field.startswith('opp'):
                            is_event_ours = not json_our_is_usao
                        else:
                            is_event_ours = json_our_is_usao
                        if is_event_ours:
                            shots_for += 1
                            if player_key:
                                match_player_shots[player_key] += 1
                        else:
                            shots_against += 1
                    else:
                        if side.startswith('us') or side == 'us' or not side:
                            shots_for += 1
                            if player_key:
                                match_player_shots[player_key] += 1
                        else:
                            shots_against += 1
        except Exception:
            jf = None

    if not jf:
        # fallback: parse per-player from MD events using em-dash splitting
        events_block = text.split('## Tous les événements', 1)[1] if '## Tous les événements' in text else text
        seen_events = set()
        for line in events_block.splitlines():
            line = line.strip()
            if not line.startswith('-'):
                continue
            parts = [p.strip() for p in line.split('—')]
            if not parts:
                continue
            mmin = re.search(r"(\d+)'", parts[0])
            if not mmin:
                continue
            minute = int(mmin.group(1))
            etype = parts[1] if len(parts) > 1 else ''
            player_raw = ''
            side = ''
            for p in parts[2:]:
                b = re.search(r"^(.*?)\s*\[([^\]]+)\]", p)
                if b:
                    player_raw = b.group(1).strip()
                    side = b.group(2).strip().lower()
                    break
            if not player_raw:
                for p in parts[2:]:
                    if '[US' in p or '[OPP' in p or '[OUR' in p.lower():
                        b = re.match(r"(.*)\[", p)
                        if b:
                            player_raw = b.group(1).strip()
                            s = re.search(r"\[([^\]]+)\]", p)
                            if s:
                                side = s.group(1).strip().lower()
                            break

            raw_name = player_raw
            matched = match_player_to_roster(raw_name, roster) if raw_name else None
            if not matched and raw_name in canonical_map:
                player_key = canonical_map[raw_name]
            else:
                player_key = matched or raw_name
            key = (minute, player_key, etype.lower())
            if key in seen_events:
                continue
            seen_events.add(key)
            is_goal = 'but' in etype.lower()
            is_shot = any(k in etype.lower() for k in ['tir', 'poteau', 'but', 'arrêt'])
            if is_goal:
                if side.startswith('us') or side == 'us' or not side:
                    us_count += 1
                    if player_key:
                        match_player_goals[player_key] += 1
                else:
                    opp_count += 1
            if is_shot:
                if side.startswith('us') or side == 'us' or not side:
                    shots_for += 1
                    if player_key:
                        match_player_shots[player_key] += 1
                else:
                    shots_against += 1

    # Prefer scores from the dated JSON when available and map team1/team2 -> our/opponent
    uf = None
    of = None
    # jdata may exist if we successfully read a JSON earlier
    if 'jdata' in locals() and isinstance(jdata, dict):
        # case: explicit score1/score2
        s1 = jdata.get('score1')
        s2 = jdata.get('score2')
        if s1 is not None and s2 is not None:
            # determine which side is our team
            t1 = (jdata.get('team1') or '').lower()
            t2 = (jdata.get('team2') or '').lower()
            our_team_field = (jdata.get('our_team') or '').lower()
            # heuristic: if our_team_field matches t1 then score1 is ours
            if our_team_field and our_team_field in t1:
                uf = int(s1)
                of = int(s2)
            elif our_team_field and our_team_field in t2:
                uf = int(s2)
                of = int(s1)
            else:
                # fallback: if t2 contains 'usao' it's ours
                if 'usao' in t1:
                    uf = int(s1)
                    of = int(s2)
                elif 'usao' in t2:
                    uf = int(s2)
                    of = int(s1)
                else:
                    # if our_team not clear, assume team2 is USAO (common pattern)
                    uf = int(s2)
                    of = int(s1)
        else:
            # case: score dict e.g. {'usao':16, 'orgeotoise':3} or 'score': {...}
            score_blob = jdata.get('score') or jdata.get('score_dict')
            if isinstance(score_blob, dict):
                # try to find a key that matches 'usao' or 'usao u8' or our_team
                our_team_field = (jdata.get('our_team') or '').lower()
                found = False
                for k, v in score_blob.items():
                    if our_team_field and our_team_field in str(k).lower():
                        uf = int(v)
                        found = True
                        break
                if not found:
                    for k, v in score_blob.items():
                        if 'usao' in str(k).lower():
                            uf = int(v)
                            found = True
                            break
                if found:
                    # pick opponent as the other value (first non-matching)
                    for k, v in score_blob.items():
                        if uf != int(v):
                            of = int(v)
                            break
    # if JSON didn't provide scores, fall back to MD header or event counts
    if uf is None:
        if us_goals is not None:
            uf = us_goals
        else:
            uf = us_count
    if of is None:
        if opp_goals is not None:
            of = opp_goals
        else:
            of = opp_count

    # team shots: compute from JSON when present, else from header (buts + tirs_hors_buts)
    if 'jdata' in locals() and isinstance(jdata, dict) and isinstance(jdata.get('shots'), dict):
        shots_blob = jdata.get('shots')
        # on_target + off_target if present
        on = shots_blob.get('on_target') or shots_blob.get('on') or 0
        off = shots_blob.get('off_target') or shots_blob.get('off') or 0
        # total shots for ours assumed in jdata as total for our side if mapping known
        shots_for = int(on) + int(off)
    else:
        if us_tirs_hors_buts is not None:
            shots_for = uf + us_tirs_hors_buts
        if opp_tirs_hors_buts is not None:
            shots_against = of + opp_tirs_hors_buts

    summary['goals_for'] += uf
    summary['goals_against'] += of
    if uf > of:
        summary['wins'] += 1
    elif uf == of:
        summary['draws'] += 1
    else:
        summary['losses'] += 1

    summary['shots_for'] += shots_for
    summary['shots_against'] += shots_against

    per_match.append({'file': f, 'date': date, 'us': uf, 'them': of, 'shots_for': shots_for, 'shots_against': shots_against})
    # merge per-match attributed player stats into global counters
    for k, v in match_player_goals.items():
        player_goals[k] += v
    for k, v in match_player_shots.items():
        player_shots[k] += v

# collapse keys: if canonical_map maps some raw keys present in counters, merge them
def collapse_counters(counter):
    new = Counter()
    for k, v in counter.items():
        if k in canonical_map:
            new[canonical_map[k]] += v
        else:
            new[k] += v
    return new

player_goals = collapse_counters(player_goals)
player_shots = collapse_counters(player_shots)

# top scorers
top_scorers = player_goals.most_common(20)

# per-player efficiency
player_eff = {}
for p, g in player_goals.items():
    shots = player_shots.get(p, 0)
    eff = f"{(g/shots*100):.1f}%" if shots > 0 else 'N/A'
    player_eff[p] = {'goals': g, 'shots': shots, 'eff': eff}

# build markdown
md_lines = []
md_lines.append('# Season Review 2025 — U8')
md_lines.append('')
md_lines.append('## Résumé chiffré')
md_lines.append('')
md_lines.append(f"- Matches analysés: **{summary['matches']}**")
md_lines.append(f"- Victoires: **{summary['wins']}**, Nuls: **{summary['draws']}**, Défaites: **{summary['losses']}**")
md_lines.append(f"- Buts pour: **{summary['goals_for']}** ({summary['goals_for']/max(1,summary['matches']):.1f} / match)")
md_lines.append(f"- Buts contre: **{summary['goals_against']}** ({summary['goals_against']/max(1,summary['matches']):.1f} / match)")
md_lines.append(f"- Tirs pour: **{summary['shots_for']}** ({summary['shots_for']/max(1,summary['matches']):.1f} / match)")
md_lines.append(f"- Tirs contre: **{summary['shots_against']}** ({summary['shots_against']/max(1,summary['matches']):.1f} / match)")
md_lines.append('')
md_lines.append('## Top buteurs')
md_lines.append('')
md_lines.append('| Rang | Joueur | Buts | Tirs | Efficacité |')
md_lines.append('|---:|---|---:|---:|---:|')
rank = 1
for p, g in top_scorers:
    shots = player_shots.get(p, 0)
    eff = player_eff.get(p, {}).get('eff', 'N/A')
    md_lines.append(f'| {rank} | {p} | {g} | {shots} | {eff} |')
    rank += 1

md_lines.append('')
md_lines.append('## Par match (synthèse)')
md_lines.append('')
md_lines.append('| Date | Score (Nous - Eux) | Tirs Nous | Tirs Eux |')
md_lines.append('|---|---:|---:|---:|')
for m in per_match:
    d = m.get('date') or m.get('file')
    md_lines.append(f"| {d} | {m['us']} - {m['them']} | {m['shots_for']} | {m['shots_against']} |")

md_lines.append('')
md_lines.append('## Observations & Recommandations')
md_lines.append('')
md_lines.append('- L’équipe est très créatrice d’occasions et relativement efficace devant le but; maintenir le travail sur la finition tout en cherchant à diversifier les passeurs et finisseurs.')
md_lines.append('- Quelques matchs montrent des pertes de concentration défensive (cf. la défaite 4-11) — travailler les transitions et placements défensifs.')
md_lines.append('- Sur le plan individuel, **Nestor**, **Maxence**, **Auguste** et **Tiago** portent l’attaque; encourager des rotations et combinaisons pour ne pas être prévisible.')
md_lines.append('- Vérifier les événements sans attribution: j’ai utilisé la liste `completed-tasks/roster/U8.md` pour améliorer l’attribution; cependant quelques événements restent non attribués.')

md_lines.append('')
md_lines.append('## Caveats')
md_lines.append('')
md_lines.append('- Doublons par date ignorés automatiquement (par ex. fichiers avec la même date).')
md_lines.append('- Les attributions reposent sur une heuristique de correspondance des noms à partir de `completed-tasks/roster/U8.md`. Si vous avez des orthographes complètes ou préférées, fournissez-les pour améliorer la précision.')

out_md = '\n'.join(md_lines)
out_path = 'completed-tasks/competitions/season_review_2025.md'
with open(out_path, 'w', encoding='utf-8') as fh:
    fh.write(out_md)

import csv
csv_path = 'completed-tasks/competitions/stats_per_player_2025.csv'
with open(csv_path, 'w', encoding='utf-8', newline='') as cf:
    writer = csv.writer(cf)
    writer.writerow(['player', 'goals', 'shots', 'eff_pct'])
    for p, g in player_goals.most_common():
        shots = player_shots.get(p, 0)
        eff = f"{(g/shots*100):.1f}%" if shots>0 else 'N/A'
        writer.writerow([p, g, shots, eff])

print(json.dumps({'out': out_path, 'csv': csv_path, 'summary': summary, 'top_scorers': top_scorers}, ensure_ascii=False, indent=2))
