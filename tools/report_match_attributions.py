import json
import glob
import os
import re
from collections import Counter


def extract_date_from_filename(fname):
    m = re.search(r'(\d{4}-\d{2}-\d{2})', fname)
    if m:
        return m.group(1)
    m = re.search(r'(\d{8})', fname)
    if m:
        s = m.group(1)
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    return None


root_files = glob.glob('completed-tasks/competitions/match_reports/**/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md', recursive=True)
rows = []
for md in sorted(root_files):
    date = extract_date_from_filename(md)
    folder = os.path.dirname(md)
    # prefer json with date in name
    json_candidates = glob.glob(os.path.join(folder, '*.json'))
    jf = None
    if json_candidates:
        if date:
            for c in json_candidates:
                if date in os.path.basename(c):
                    jf = c
                    break
        if not jf:
            for c in json_candidates:
                if os.path.basename(c).lower().startswith('match_'):
                    jf = c
                    break
        if not jf:
            jf = json_candidates[0]
    if not jf:
        print(f"{date or md}: no json found in {folder}")
        continue
    try:
        with open(jf, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
    except Exception as e:
        print(f"{date or md}: failed to read json {jf}: {e}")
        continue
    events = data.get('events', [])
    goals_by_player = Counter()
    shots_by_player = Counter()
    unassigned_goals = 0
    unassigned_shots = 0
    total_us_goals = 0
    total_us_shots = 0
    for e in events:
        etype = (e.get('type') or '').lower()
        team = (e.get('team') or '').lower()
        player = e.get('player')
        is_goal = 'but' in etype or e.get('classification') == 'goal'
        is_shoot = e.get('classification') == 'shoot' or any(k in etype for k in ['tir', 'frappe', 'poteau', 'arrêt'])
        # consider only our team's events
        is_ours = (team and team.startswith('us')) or (not team and e.get('side') and e.get('side') in ['left', 'right'])
        if is_goal and is_ours:
            total_us_goals += 1
            if player:
                goals_by_player[player] += 1
            else:
                unassigned_goals += 1
        if is_shoot and is_ours:
            total_us_shots += 1
            if player:
                shots_by_player[player] += 1
            else:
                unassigned_shots += 1
    print('---')
    print(f"{date}  JSON: {os.path.basename(jf)}")
    print(f"us goals extracted: {total_us_goals} (assigned: {sum(goals_by_player.values())}, unassigned: {unassigned_goals})")
    if goals_by_player:
        for p, c in goals_by_player.most_common():
            s = shots_by_player.get(p, 0)
            print(f"  - {p}: {c} goals, {s} shots")
    else:
        print("  - no assigned goals")

print('---\nDone')
