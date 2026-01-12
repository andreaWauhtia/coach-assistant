#!/usr/bin/env python3
"""
Script to parse Markdown tables of match events and lineup into JSON format for performance analysis.

Usage: python tools/parse_markdown_table.py events.md output.json --lineup lineup.md
"""

import argparse
import json
import re

def parse_markdown_table(markdown_text):
    """
    Parse the Markdown table into match_info and events.
    """
    lines = markdown_text.strip().split('\n')
    
    # Find the table start
    header_line = None
    data_start = None
    for i, line in enumerate(lines):
        if line.startswith('|') and '---' not in line and header_line is None:
            header_line = i
        elif line.startswith('| ---') and header_line is not None:
            data_start = i + 1
            break
    
    if header_line is None or data_start is None:
        raise ValueError("Invalid Markdown table format")
    
    # Parse header
    header = [col.strip() for col in lines[header_line].split('|')[1:-1]]
    
    # Parse data rows
    events = []
    match_info = {}
    for line in lines[data_start:]:
        if not line.strip() or not line.startswith('|'):
            continue
        cols = [col.strip() for col in line.split('|')[1:-1]]
        if len(cols) != len(header):
            continue
        
        row = dict(zip(header, cols))
        
        # Extract match info from first row
        if not match_info:
            match_info = {
                'match_date': row.get('match_date', ''),
                'result': row.get('result', ''),
                'is_home': row.get('is_home', '').lower() == 'true'
            }
        
        # Create event
        event = {}
        
        # Minute (convert seconds to minutes)
        timecode = int(row.get('timecode', 0))
        event['minute'] = timecode // 60
        
        # Type mapping
        action_type = row.get('action_type', '')
        type_mapping = {
            'Goal': 'But',
            'Shoot off target': 'Tir à côté',
            'Shoot on target': 'Tir cadré',
            'Post': 'Poteau',
            'Pass': 'Passe',
            'Duel': 'Duel',
            'Tackle': 'Tacle',
            'Interception': 'Interception',
            'Foul suffered': 'Fautes subies',
            'Key pass': 'Passe décisive',
            'Assist': 'Passe décisive',
        }
        event['type'] = type_mapping.get(action_type, action_type)
        
        # Player
        first_name = row.get('first_name', '').strip()
        last_name = row.get('last_name', '').strip()
        if first_name and first_name.lower() != 'null' and last_name and last_name.lower() != 'null':
            event['player'] = f"{first_name} {last_name}"
        elif (first_name and first_name.lower() != 'null') or (last_name and last_name.lower() != 'null'):
            event['player'] = (first_name or last_name).strip()
        else:
            # Opponent event
            if row.get('from_opponent', '').lower() == 'true':
                event['player'] = "Adversaire"
            else:
                event['player'] = None
        
        # Side
        from_opponent = row.get('from_opponent', '').lower() == 'true'
        if match_info['is_home']:
            event['side'] = 'right' if from_opponent else 'left'
        else:
            event['side'] = 'left' if from_opponent else 'right'
        
        # Assist
        note = row.get('note', '')
        if 'Vers:' in note:
            assist_match = re.search(r'Vers:\s*([^,]+)', note)
            if assist_match:
                event['assist'] = assist_match.group(1).strip()
        
        # Action result
        action_result = row.get('action_result', '')
        if action_result and action_result != 'null':
            event['result'] = action_result
        
        events.append(event)
    
    return match_info, events

    main()

def get_position(line, slot):
    """
    Map line and slot to position label.
    """
    # Line 0: GK
    if line == 0:
        return 'GK'

    # Line 1: Defense
    if line == 1:
        positions = {
            1: 'DC',
            2: 'DD',
            3: 'DG',
            4: 'DC',
            5: 'DC'
        }
        return positions.get(slot, 'DEF')

    # Line 2: Defensive Midfield
    if line == 2:
        positions = {
            1: 'MDC',
            2: 'MD',
            3: 'MG',
            4: 'MDC'
        }
        return positions.get(slot, 'MDef')

    # Line 3: Midfield
    if line == 3:
        positions = {
            1: 'MC',
            2: 'MD',
            3: 'MG',
            4: 'MC'
        }
        return positions.get(slot, 'MIL')

    # Line 4: Attack
    if line == 4:
        positions = {
            1: 'BU',
            2: 'AD',
            3: 'AG'
        }
        return positions.get(slot, 'ATT')

    return None

def parse_lineup_table(markdown_text):
    """
    Parse the lineup table into a list of player dicts.
    """
    lines = markdown_text.strip().split('\n')
    
    # Find the table start
    header_line = None
    data_start = None
    for i, line in enumerate(lines):
        if line.startswith('|') and '---' not in line and header_line is None:
            header_line = i
        elif line.startswith('| ---') and header_line is not None:
            data_start = i + 1
            break
    
    if header_line is None or data_start is None:
        raise ValueError("Invalid lineup table format")
    
    # Parse header
    header = [col.strip() for col in lines[header_line].split('|')[1:-1]]
    
    # Parse data rows
    lineup = []
    for line in lines[data_start:]:
        if not line.strip() or not line.startswith('|'):
            continue
        cols = [col.strip() for col in line.split('|')[1:-1]]
        if len(cols) != len(header):
            continue
        
        row = dict(zip(header, cols))
        
        player = {}
        first_name = row.get('first_name', '').strip()
        last_name = row.get('last_name', '').strip()
        if first_name and first_name.lower() != 'null' and last_name and last_name.lower() != 'null':
            player['name'] = f"{first_name} {last_name}"
        else:
            continue
        
        player['line'] = int(row.get('line', 0))
        player['position_slot'] = int(row.get('position_slot', 0))
        player['entry_timecode'] = int(row.get('entry_timecode', 0))
        exit_timecode = row.get('exit_timecode', '').strip()
        player['exit_timecode'] = int(exit_timecode) if exit_timecode and exit_timecode.lower() != 'null' else None
        
        # Add position
        position = get_position(player['line'], player['position_slot'])
        if position:
            player['position'] = position
        
        lineup.append(player)
    
    return lineup

def generate_json(match_info, events, lineup=None):
    """
    Generate the final JSON structure.
    """
    # Determine teams from result and is_home
    result = match_info['result']
    if '-' in result:
        scores = result.split('-')
        home_score = int(scores[0])
        away_score = int(scores[1])
        if match_info['is_home']:
            home_team = "Notre Équipe"  # Placeholder, should be configurable
            away_team = match_info.get('opponent_name', 'Adversaire')
        else:
            away_team = "Notre Équipe"
            home_team = match_info.get('opponent_name', 'Adversaire')
        
        match_header = f"{home_team} {home_score}-{away_score} {away_team}"
    else:
        match_header = f"Match - {result}"
    
    structure = "HOME (left) | TIMELINE | AWAY (right)."
    if match_info['is_home']:
        structure += f" {match_info.get('opponent_name', 'Adversaire')} LEFT, Notre Équipe RIGHT (NOUS)"
    else:
        structure += f" Notre Équipe LEFT, {match_info.get('opponent_name', 'Adversaire')} RIGHT (NOUS)"
    
    json_data = {
        "match_header": match_header,
        "match_date": match_info['match_date'],
        "structure": structure,
        "events": events
    }
    if lineup:
        json_data["lineup"] = lineup
    return json_data

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Parse Markdown tables to JSON")
    parser.add_argument('events_file', help='Markdown file with events table')
    parser.add_argument('output_file', help='Output JSON file')
    parser.add_argument('--lineup', help='Markdown file with lineup table')
    
    args = parser.parse_args()
    
    # Parse events
    with open(args.events_file, 'r', encoding='utf-8') as f:
        events_text = f.read()
    match_info, events = parse_markdown_table(events_text)
    
    # Parse lineup if provided
    lineup = None
    if args.lineup:
        with open(args.lineup, 'r', encoding='utf-8') as f:
            lineup_text = f.read()
        lineup = parse_lineup_table(lineup_text)
    
    # Generate JSON
    json_data = generate_json(match_info, events, lineup)
    
    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()