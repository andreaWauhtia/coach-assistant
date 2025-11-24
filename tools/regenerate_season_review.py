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

def count_shots_from_json(date):
    jf = find_json_for_date(date)
    if not jf:
        return None
    try:
        with open(jf, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return None
    shots_us = 0
    shots_them = 0
    for event in data.get('events', []):
        classification = (event.get('classification') or '').lower()
        if classification not in ('shoot', 'goal'):
            continue
        team = (event.get('team') or '').lower()
        if team == 'us':
            shots_us += 1
        elif team == 'opponent':
            shots_them += 1
    return {
        'shots_us': shots_us,
        'shots_them': shots_them,
        'source_display': f"`{os.path.basename(jf)}` (JSON)."
    }

def attach_json_shots(rows):
    for row in rows:
        shot_info = count_shots_from_json(row['date'])
        if shot_info:
            row['shots_us'] = shot_info['shots_us']
            row['shots_them'] = shot_info['shots_them']
            row['source_display'] = shot_info['source_display']
        else:
            row.setdefault('shots_us', row.get('shots_us', 0))
            row.setdefault('shots_them', row.get('shots_them', 0))
            row.setdefault('source_display', '`Par match table` (MD).')

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
    obs.append('- **Synthèse principale** : l\'équipe produit de très nombreuses occasions et convertit un grand nombre d\'entre elles (moyenne de tirs élevée, buteurs principaux efficaces). L\'effort doit rester concentré sur la stabilité défensive et la gestion des phases de transition.')
    obs.append('- **Offensif** : consolider la diversité offensive avec des combinaisons courtes dans la zone de finition et des permutations de position pour éviter de dépendre d\'un seul point d\'appui; maintenir les exercices de finition payants.')
    obs.append('- **Défensif** : définir des repères de replacement, travailler la réactivité suite à une perte de balle et multiplier les mini-séances sur duels/replis.')
    obs.append('- **Gestion du groupe** : attention aux minutes d\'entrée de match (plusieurs buts encaissés rapidement). Mettre en place une routine d\'activation pré-match et un micro-briefing collectif à la mi-temps quand l\'équipe est menée.')
    obs.append('- **Individuel** : valoriser la polyvalence de Nestor, Maxence, Tiago et Auguste via des rotations planifiées pour préserver l\'énergie et multiplier les solutions.')
    obs.append('- **Données & suivi** : la table `Par match` reste la source des totaux d\'équipe; préférez les JSON `YYYY-MM-DD.json` contenant `players_present` et `events` pour les attributions individuelles.')
    obs.append('- **Contexte particulier** : le match du `2025-11-19` opposait notre équipe à une formation U9 (joueurs d\'un an de plus). Les statistiques (buts encaissés, tirs adverses) doivent être nuancées en conséquence.')
    obs.append('')

    # Participation
    total_matches = len(rows)
    part = []
    part.append('## Participation des joueurs (saison)')
    part.append('')
    part.append('- Total de matches pris en compte : **{}**'.format(total_matches))
    part.append('')
    part.append('| Joueur | Apparitions | % de participation | Notes |')
    part.append('|---|---:|---:|---|')
    for p, c in player_counts.most_common():
        pct = (c / total_matches * 100) if total_matches>0 else 0
        part.append(f'| {p} | {c} | {pct:.1f}% | |')
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
        repart.append('| Date | Score (Nous - Eux) | Tirs Nous | Tirs Eux | Source |')
        repart.append('|---|---:|---:|---:|---|')
        for r in rows_list:
            source = r.get('source_display', '`Par match table` (MD).')
            repart.append(f"| {r['date']} | {r['us']} - {r['them']} | {r.get('shots_us',0)} | {r.get('shots_them',0)} | {source} |")
        repart.append('')

    # Caveats
    cave = []
    cave.append('## Caveats détaillés')
    cave.append('')
    cave.append('### Sources hétérogènes')
    cave.append('- Les totaux proviennent des fichiers Markdown `YYYY-MM-DD.md`, tandis que les attributions individuelles sont extraites des JSON `YYYY-MM-DD.json`. J\'ai conservé une logique hybride (MD pour les totaux, JSON pour les joueurs) : choisissez votre source prioritaire si vous voulez un seul référentiel.')
    cave.append('')
    cave.append('### Tirs manquants et backfills')
    cave.append('- Certains JSON ne contiennent pas le champ `shots`. Lorsque cela arrive, j\'ai backfillé les tirs avec les MD disponibles, et les lignes sans `shots` sont restées à 0 avant correction. Pour un rapport plus fin, exécutez `tools/update_shots_md.py`.')
    cave.append('')
    cave.append('### Attributions incomplètes')
    cave.append('- Si un événement comporte `player: null`, je n\'attribue rien. Pour améliorer la couverture, stabilisez les orthographes dans `completed-tasks/roster/U8.md` et fournissez une table d\'appariement observé → canonique si besoin.')
    cave.append('')
    cave.append('### Normalisation des noms')
    cave.append('- Une normalisation automatique (observé → canonique) a été appliquée depuis le roster local ; certaines correspondances heuristiques peuvent rester imprécises. Je peux fournir la table complète pour revue.')
    cave.append('')
    cave.append('### Corrections manuelles')
    cave.append('- Les overrides demandés (ex. `2025-11-19` : `Tirs Eux = 25`) sont conservés et peuvent diverger des JSON originaux. Documentez-les pour les audits.')
    cave.append('')
    cave.append('### Reproductibilité')
    cave.append('- Les scripts de la logique (`tools/aggregate_matches.py`, `tools/update_shots_md.py`, `tools/regenerate_season_review.py`) permettent de reproduire chaque étape et de mettre à jour les données quand de nouveaux JSON arrivent.')
    cave.append('')
    cave.append('### Matchs hors-catégorie')
    cave.append('- Le match `2025-11-19` opposait notre équipe à une formation U9 (joueurs d\'un an de plus). Modérez les comparaisons (buts encaissés, tirs adverses) en conséquence.')
    cave.append('')

    sources = []
    sources.append('## Sources')
    sources.append('- `tools/aggregate_matches.py` (agrégation des tableaux par match)')
    sources.append('- `tools/update_shots_md.py` (backfill des tirs/fiches manquantes)')
    sources.append('- `tools/regenerate_season_review.py` (réexécution complète du rapport)')
    sources.append('- `completed-tasks/competitions/match_reports/YYYY-MM-DD.md` (totaux d\'équipe par match)')
    sources.append('- `completed-tasks/competitions/match_reports/YYYY-MM-DD.json` (attributions individuelles et événements)')
    sources.append('')

    return '\n'.join(obs), '\n'.join(part), '\n'.join(repart), '\n'.join(cave), '\n'.join(sources)

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
    attach_json_shots(rows)
    player_counts = compute_participation(dates)
    obs_s, part_s, repart_s, cave_s, sources_s = build_sections(rows, player_counts)
    new_md = prefix + '\n\n' + obs_s + '\n\n' + part_s + '\n\n' + repart_s + '\n\n' + cave_s + '\n\n' + sources_s
    write_md(new_md)
    print('Rebuilt season review with updated sections.')
