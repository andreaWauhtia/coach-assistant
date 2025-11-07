#!/usr/bin/env python3
"""Parse SportEasy timeline data into structured events with team classification.

This tool processes manually-read timeline data from SportEasy screenshots.
You provide raw event data (minute, event type, player, side), and the tool:
  1. Parses the header to identify teams and score
  2. Classifies events by side (our team vs opponent)
  3. Infers additional context (shots that resulted in saves = opponent shots on us)
  4. Exports to CSV and Markdown report

Usage:
  python tools/parse_timeline.py --input timeline_data.json --out-dir .memory-bank/competitions

Input format (JSON):
{
  "match_header": "R.St.FC.Bouillon 4-12 USAO U8 2025/2026",
  "our_team": "R.St.FC.Bouillon",
  "events": [
    {"minute": 5, "type": "Tir arrêté", "player": "Lilou Douny", "side": "left"},
    {"minute": 4, "type": "But", "player": "Nestor Arnould", "side": "left"},
    ...
  ]
}

Or use --interactive mode to enter data interactively.

Saves:
  - CSV with classified events: {out_dir}/parsed_by_side.csv
  - Markdown report: {out_dir}/{matchday}.md
"""
import argparse
import csv
import json
import re
from pathlib import Path
from datetime import datetime


# Event keywords by category
EVENT_KEYWORDS = [
    "But",
    "Carton Jaune",
    "Carton Rouge",
    "Remplacement",
    "Arrêt",
    "Tir à côté",
    "Poteau",
    "Transversale",
    "Tir arrêté",
    "Blessé"
]

# Events that represent shots
SHOOT_KEYWORDS = {"Tir à côté", "Poteau", "Transversale", "Arrêt", "Tir arrêté"}

# Header pattern to extract teams and score
# Format: "Team1 Name" | "score1 - score2" | "Team2 Name season"
HEADER_RE = re.compile(
    r"^(.*?)\s*[\|\-]\s*(\d+)\s*\-\s*(\d+)\s*[\|\-]\s*(.*?)(?:\s+\d{4}/\d{4})?$",
    re.MULTILINE
)

MINUTE_RE = re.compile(r"(\d{1,2})\s*'")


def load_events_from_json(json_path):
    """Load manually-read timeline events from JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Cannot load JSON from {json_path}: {e}")


def parse_header(text_or_dict):
    """Extract teams and score from header text or dict.
    
    Can parse:
      - Text: "R.St.FC.Bouillon 4-12 USAO U8 2025/2026"
      - Dict with 'match_header' or 'header' key
    
    Returns: {
        'team1': str,      # Left team (us)
        'team2': str,      # Right team (opponent)
        'score1': int,     # Our team score
        'score2': int,     # Opponent team score
    }
    """
    header_text = text_or_dict
    if isinstance(text_or_dict, dict):
        header_text = text_or_dict.get('match_header') or text_or_dict.get('header', '')
    
    # Try to match pattern: "Team1 score1-score2 Team2 ..."
    # More flexible pattern for French team names with dots and numbers
    # Strategy: find the score pattern (digits-digits) and work backwards/forwards
    patterns = [
        # Pattern: Match "...anything... DIGIT(s)-DIGIT(s) ...anything..."
        # Use non-greedy matching to capture teams
        r'^(.+?)\s+(\d+)\s*[\-\–]\s*(\d+)\s+(.+?)(?:\s+\d{4}/\d{4})?$',
        # Pattern: "Team | score-score | Team"
        r'^([^|]+?)\s*\|\s*(\d+)\s*[\-\–]\s*(\d+)\s*\|\s*(.+)$',
    ]
    
    for pattern in patterns:
        m = re.search(pattern, header_text.strip(), re.MULTILINE)
        if m:
            try:
                return {
                    'team1': m.group(1).strip(),
                    'score1': int(m.group(2)),
                    'score2': int(m.group(3)),
                    'team2': m.group(4).strip(),
                }
            except (ValueError, IndexError):
                pass
    
    # Fallback: return empty
    return {'team1': None, 'score1': None, 'score2': None, 'team2': None}


def classify_and_enrich_events(events_list, our_team_name, opponent_team_name, our_team_side=None):
    """Classify events by team and add inferred actions.
    
    Args:
        events_list: List of {minute, type, player, side} dicts
        our_team_name: Name of our team
        opponent_team_name: Name of opponent team
        our_team_side: 'left' if we are HOME, 'right' if we are AWAY, None for auto-detect
    
    Returns:
        List of enriched events with: minute, type, player, side, team, 
        classification, inferred_actions, confidence
    """
    enriched = []
    
    for event in events_list:
        e = dict(event)  # Copy
        
        minute = e.get('minute')
        event_type = e.get('type', '').strip()
        side = e.get('side', '').lower() if isinstance(e.get('side'), str) else None
        player = e.get('player', '')
        
        # Determine team based on side
        # Our side is flexible: could be 'left' (HOME) or 'right' (AWAY)
        if our_team_side == 'left':
            # We are HOME team (left side)
            if side == 'left':
                team = 'us'
            elif side == 'right':
                team = 'opponent'
            else:
                team = None
        elif our_team_side == 'right':
            # We are AWAY team (right side)
            if side == 'right':
                team = 'us'
            elif side == 'left':
                team = 'opponent'
            else:
                team = None
        else:
            # Default fallback (legacy behavior)
            if side == 'left':
                team = 'opponent'
            elif side == 'right':
                team = 'us'
            else:
                team = None
        
        # Classify event
        classification = None
        if event_type == 'But':
            classification = 'goal'
        elif event_type in SHOOT_KEYWORDS:
            classification = 'shoot'
        elif event_type == 'Remplacement':
            classification = 'substitution'
        elif event_type in ('Carton Jaune', 'Carton Rouge'):
            classification = 'card'
        elif event_type == 'Blessé':
            classification = 'injury'
        
        # Infer additional actions
        inferred_actions = []
        if team == 'us':
            # If we had a save or blocked shot, we conceded an opponent shot
            if event_type in ('Arrêt', 'Tir arrêté'):
                inferred_actions.append('frappe_subite')  # opponent shot on us
        elif team == 'opponent':
            # If opponent had a save or blocked shot, we had a shot
            if event_type in ('Arrêt', 'Tir arrêté'):
                inferred_actions.append('frappe_créée')  # we shot
        
        # Confidence: higher if player name present and classification found
        confidence = 0.5
        if player and len(player.strip()) > 0:
            confidence += 0.25
        if classification:
            confidence += 0.25
        confidence = min(1.0, confidence)
        
        enriched.append({
            'minute': minute,
            'type': event_type,
            'player': player.strip() if player else None,
            'side': side,
            'team': team,
            'classification': classification,
            'inferred_actions': inferred_actions,
            'confidence': confidence,
        })
    
    return enriched


def parse_text(text, header=None):
    """Legacy function: parse text for backward compatibility.
    Not used in current workflow (we use JSON input instead).
    """
    pass


def export_to_csv(enriched_events, out_path):
    """Export classified events to CSV.
    
    Columns: minute, type, player, side, team, classification, inferred_actions, confidence
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                'minute', 'type', 'player', 'side', 'team', 
                'classification', 'inferred_actions', 'confidence'
            ]
        )
        writer.writeheader()
        for event in enriched_events:
            writer.writerow({
                'minute': event['minute'] or '',
                'type': event['type'],
                'player': event['player'] or '',
                'side': event['side'] or '',
                'team': event['team'] or '',
                'classification': event['classification'] or '',
                'inferred_actions': ';'.join(event.get('inferred_actions', [])),
                'confidence': f"{event.get('confidence', 0):.2f}",
            })
    
    return out_path


def build_report(enriched_events, header_info, matchday, out_dir):
    """Generate Markdown report from classified events."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    team1 = header_info.get('team1', 'Team 1')
    team2 = header_info.get('team2', 'Team 2')
    score1 = header_info.get('score1', 0)
    score2 = header_info.get('score2', 0)
    
    # Count metrics
    our_goals = sum(1 for e in enriched_events 
                    if e['team'] == 'us' and e['classification'] == 'goal')
    opponent_goals = sum(1 for e in enriched_events 
                         if e['team'] == 'opponent' and e['classification'] == 'goal')
    
    our_shots = sum(1 for e in enriched_events 
                    if e['team'] == 'us' and e['classification'] == 'shoot')
    opponent_shots = sum(1 for e in enriched_events 
                         if e['team'] == 'opponent' and e['classification'] == 'shoot')
    
    # Group by minute
    by_minute = {}
    for e in enriched_events:
        m = e.get('minute') or 0
        key = (m // 5) * 5
        by_minute.setdefault(key, [])
        by_minute[key].append(e)
    
    md_lines = []
    md_lines.append(f"# Match: {team1} {score1} - {score2} {team2}")
    md_lines.append(f"*Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    md_lines.append("## Résumé")
    md_lines.append(f"- **{team1}**: {opponent_goals} buts, {opponent_shots} tirs")
    md_lines.append(f"- **{team2}**: {our_goals} buts, {our_shots} tirs\n")
    
    md_lines.append("## Distribution temporelle (par tranche 5')\n")
    for min_key in sorted(by_minute.keys()):
        events_in_slot = by_minute[min_key]
        md_lines.append(f"**{min_key}'-{min_key+4}'**: {len(events_in_slot)} événements")
        for e in events_in_slot:
            player_str = f" ({e['player']})" if e['player'] else ""
            team_str = f" [{e['team'].upper()}]" if e['team'] else ""
            md_lines.append(f"  - {e['type']}{player_str}{team_str}")
        md_lines.append("")
    
    md_lines.append("## Tous les événements\n")
    for e in enriched_events:
        minute_str = f"{e['minute']:2d}'" if e['minute'] is not None else "?"
        player_str = f" — {e['player']}" if e['player'] else ""
        team_str = f" [{e['team'].upper()}]" if e['team'] else ""
        inferred_str = f" (inféré: {', '.join(e['inferred_actions'])})" if e['inferred_actions'] else ""
        md_lines.append(
            f"- {minute_str} — {e['type']}{player_str}{team_str}"
            f" — {e['classification'] or '?'}{inferred_str}"
        )
    
    out_path = out_dir / f"{matchday}.md"
    out_path.write_text('\n'.join(md_lines), encoding='utf-8')
    return out_path


def main():
    ap = argparse.ArgumentParser(
        description='Parse and classify SportEasy timeline events by team'
    )
    ap.add_argument(
        '--input', '-i',
        help='JSON file with timeline data (or use --interactive for manual entry)'
    )
    ap.add_argument(
        '--interactive', '-I',
        action='store_true',
        help='Interactive mode: enter events manually'
    )
    ap.add_argument(
        '--out-dir', '-o',
        default='.memory-bank/competitions',
        help='Base directory for outputs (final outputs will be under {out_dir}/analysis/{matchday})'
    )
    ap.add_argument(
        '--matchday', '-m',
        default=None,
        help='Match identifier (used in output filenames)'
    )
    ap.add_argument(
        '--our-team', '-t',
        default=None,
        help='Name of our team (auto-detected from header if not provided)'
    )
    args = ap.parse_args()
    
    events_data = None
    
    # Load events
    if args.input:
        print(f"Loading events from {args.input}...")
        events_data = load_events_from_json(args.input)
    elif args.interactive:
        events_data = prompt_interactive_input()
    else:
        ap.print_help()
        return 1
    
    # Parse header
    header_info = parse_header(events_data)
    print(f"\n📋 Match: {header_info.get('team1', '?')} {header_info.get('score1', '?')}"
          f" - {header_info.get('score2', '?')} {header_info.get('team2', '?')}")
    
    # Get our team name - determine which side we're on
    our_team = args.our_team
    team1 = header_info.get('team1')
    team2 = header_info.get('team2')
    
    # Auto-detect our team position if --our-team is provided
    if our_team:
        # Check if our team matches team1 or team2
        if our_team.lower().strip() == (team1 or '').lower().strip():
            opponent_team = team2
            # We are HOME (team1, left)
            our_side = 'left'
        elif our_team.lower().strip() == (team2 or '').lower().strip():
            opponent_team = team1
            # We are AWAY (team2, right)
            our_side = 'right'
        else:
            print(f"⚠️  Warning: --our-team '{our_team}' doesn't match header teams")
            opponent_team = team2 if our_team != team1 else team1
            our_side = None
    else:
        # Fallback: assume team1 is ours
        our_team = team1
        opponent_team = team2
        our_side = 'left'
    
    if not our_team:
        print("❌ Error: Cannot determine our team from header. Use --our-team flag.")
        return 1
    
    print(f"   👥 Our team: {our_team} ({'HOME/left' if our_side == 'left' else 'AWAY/right' if our_side == 'right' else '?'})")
    print(f"   👥 Opponent: {opponent_team}\n")
    
    # Classify events
    raw_events = events_data.get('events', [])
    print(f"Processing {len(raw_events)} events...")
    enriched = classify_and_enrich_events(raw_events, our_team, opponent_team, our_team_side=our_side)
    
    # Generate outputs
    base_out = Path(args.out_dir)
    matchday = args.matchday or datetime.now().strftime('%Y-%m-%d')

    # Final output directory per requirement: {base_out}/analysis/{matchday}
    final_out_dir = base_out / 'analysis' / matchday
    final_out_dir.mkdir(parents=True, exist_ok=True)

    # Write a parsed JSON representing the enriched events and header info
    parsed_json = {
        'matchday': matchday,
        'match_header': header_info.get('team1') + f" {header_info.get('score1', '')}-{header_info.get('score2', '')} " + header_info.get('team2') if header_info.get('team1') and header_info.get('team2') else header_info,
        'team1': header_info.get('team1'),
        'team2': header_info.get('team2'),
        'score1': header_info.get('score1'),
        'score2': header_info.get('score2'),
        'our_team': our_team,
        'opponent_team': opponent_team,
        'events': enriched,
    }

    json_path = final_out_dir / f"{matchday}.json"
    try:
        with open(json_path, 'w', encoding='utf-8') as jf:
            json.dump(parsed_json, jf, ensure_ascii=False, indent=2)
        print(f"✅ Parsed JSON exported: {json_path}")
    except Exception as e:
        print(f"⚠️  Warning: failed to write parsed JSON to {json_path}: {e}")

    # Export CSV
    csv_path = export_to_csv(enriched, final_out_dir / 'parsed_by_side.csv')
    print(f"✅ CSV exported: {csv_path}")

    # Export Markdown
    md_path = build_report(enriched, header_info, matchday, final_out_dir)
    print(f"✅ Report exported: {md_path}")
    
    return 0


def prompt_interactive_input():
    """Interactive mode: collect match data and events from user input."""
    print("\n=== INTERACTIVE MODE ===\n")
    
    header = input("Enter match header (e.g., 'Team1 4-12 Team2 2025/2026'): ").strip()
    if not header:
        raise ValueError("Match header is required")
    
    events = []
    print("\nEnter events one by one (leave minute empty to finish):")
    print("Format: minute type player side")
    print("  minute: number (1-90)")
    print("  type: But, Carton Jaune, Carton Rouge, Remplacement, Arrêt, Tir à côté, Poteau, Transversale, Tir arrêté, Blessé")
    print("  player: name or empty")
    print("  side: left or right\n")
    
    while True:
        minute_str = input("Minute (or empty to finish): ").strip()
        if not minute_str:
            break
        
        try:
            minute = int(minute_str)
        except ValueError:
            print("❌ Invalid minute")
            continue
        
        event_type = input("Event type: ").strip()
        if event_type not in EVENT_KEYWORDS:
            print(f"⚠️  Unknown event type. Known types: {', '.join(EVENT_KEYWORDS)}")
        
        player = input("Player (optional): ").strip() or None
        side = input("Side (left/right): ").strip().lower()
        if side not in ('left', 'right'):
            print("⚠️  Side should be 'left' or 'right'")
            side = None
        
        events.append({
            'minute': minute,
            'type': event_type,
            'player': player,
            'side': side,
        })
        print()
    
    return {
        'match_header': header,
        'events': events,
    }


if __name__ == '__main__':
    raise SystemExit(main())
