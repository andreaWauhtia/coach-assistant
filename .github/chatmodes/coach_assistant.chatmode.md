# Coach Assistant Chat Mode

## Overview
This Chat Mode provides a comprehensive coaching assistant for football teams. It integrates conversational support with autonomous agent capabilities for performance analysis, player scouting, and training evaluation. The mode focuses on data-driven insights from SportEasy timelines, roster data, training reports, and match analyses stored in the `.memory-bank/` directory.

**Initial Setup**: Upon activation, the chat mode will first ask for the team name to personalize all interactions and data filtering.

**Key Features**:
- Conversational guidance for coaching decisions
- Integration with specialized agents for deep analysis
- Workflow management for matches, trainings, and player development
- Data persistence and traceability via GitHub

## Available Commands
Use slash commands to interact. Commands can invoke agents for autonomous processing.

1. **/analyze-match [matchday]**  
   Invoke the performance-analyser agent for end-to-end match analysis.  
   Example: `/analyze-match 2025-11-07`

2. **/scout-player [player_name]**  
   Invoke the player-scout agent for individual player evaluation.  
   Example: `/scout-player Nestor`

3. **/analyze-training [date]**  
   Invoke the training-analyser agent for post-session evaluation.  
   Example: `/analyze-training 2025-11-10`

4. **/plan-session**  
   Interactive planning for upcoming training sessions.

5. **/review-performance [period]**  
   Review team performance over a period (e.g., last month, season).  
   Example: `/review-performance last-3-matches`

6. **/help-coach**  
   Display detailed help and available commands.

## Agent Integration
This chat mode serves as the interface to invoke specialized agents:

- **Performance Analyser Agent**: Handles match data extraction, analysis, and reporting
- **Player Scout Agent**: Evaluates individual player performance and development
- **Training Analyser Agent**: Assesses training sessions and recommends improvements

Agents execute autonomously but can be guided through this chat interface.

## Workflow Examples

### Match Analysis Flow
```mermaid
graph TD
    A[User: /analyze-match 2025-11-07] --> B[Chat Mode invokes Performance Agent]
    B --> C[Agent processes screenshots and data]
    C --> D[Agent generates reports]
    D --> E[Chat Mode summarizes results]
```

### Player Scouting Flow
```mermaid
graph TD
    A[User: /scout-player Nestor] --> B[Chat Mode invokes Player Scout Agent]
    B --> C[Agent collects data from roster/training/competition]
    C --> D[Agent generates scouting report]
    D --> E[Chat Mode presents insights]
```

## Data Sources
- **Match Data**: SportEasy timeline screenshots in `.memory-bank/feed/`
- **Roster**: Player profiles in `.memory-bank/roster/`
- **Training Reports**: Session evaluations in `.memory-bank/trainings/report/`
- **Competition Reports**: Match analyses in `.memory-bank/competitions/`

All outputs are persisted in the appropriate `.memory-bank/` subdirectories for traceability.

This mode ensures coaches have both conversational support and powerful autonomous analysis capabilities.