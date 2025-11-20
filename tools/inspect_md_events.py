import glob, re
from collections import Counter

files = glob.glob('completed-tasks/competitions/match_reports/**/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md', recursive=True)
player_goals = Counter()
player_shots = Counter()

line_re = re.compile(r"-\s*(\d+)'\s*[—-]\s*([^—-\n]+?)\s*[—-]\s*([^\[]]*?)\s*\[([^\]]+)\]", re.IGNORECASE)
line_re2 = re.compile(r"-\s*(\d+)'\s*[—-]\s*([^—-\n]+?)\s*[—-]\s*([^\n]+)", re.IGNORECASE)

for f in sorted(files):
    with open(f, 'r', encoding='utf-8') as fh:
        text = fh.read()
    if '## Tous les événements' in text:
        events_block = text.split('## Tous les événements', 1)[1]
    else:
        events_block = text
    for line in events_block.splitlines():
        line=line.strip()
        if not line.startswith('-'):
            continue
        m = line_re.search(line)
        if m:
            minute, etype, player_raw, side = m.groups()
            etype=etype.strip()
            player_raw=player_raw.strip()
            side=side.strip()
        else:
            m2 = line_re2.search(line)
            if m2:
                minute, etype, rest = m2.groups()
                mm = re.search(r"([^\[]+?)\s*\[([^\]]+)\]", rest)
                if mm:
                    player_raw = mm.group(1).strip()
                    side = mm.group(2).strip()
                else:
                    player_raw = ''
                    side = ''
            else:
                continue
        is_goal = 'but' in etype.lower()
        is_shot = any(k in etype.lower() for k in ['tir','poteau','arrêt','tir arrêté','tir à côté']) or is_goal
        if is_goal:
            if side.lower().startswith('us') or side.lower()=='us' or 'us' in side.lower():
                player_goals[player_raw]+=1
        if is_shot:
            if side.lower().startswith('us') or side.lower()=='us' or 'us' in side.lower():
                player_shots[player_raw]+=1

print('files:', len(files))
print('unique goalers:', len([p for p in player_goals if player_goals[p]>0]))
print('top goals:', player_goals.most_common(20))
print('top shots:', player_shots.most_common(20))
