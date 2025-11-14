# mystuff

A collection of football coaching tools and analysis scripts.

## Coach Assistant Chatbot 🏆

An intelligent chatbot for football team coaching support with natural language understanding and powerful slash commands.

### Quick Start

```python
from chatbot import ChatbotAPI

# Create a chatbot session
api = ChatbotAPI(team_name="USAO U8")

# Start chatting
response = api.send_message("Hello!")
print(response)

# Analyze a match
response = api.send_message("/analyze-match 2025-09-17")
print(response)

# Scout a player
response = api.send_message("/scout-player Nestor")
print(response)
```

### Interactive Mode

```bash
python example_chatbot.py --interactive
```

### Available Commands

- `/analyze-match [matchday]` - Analyze match statistics
- `/scout-player [player_name]` - Evaluate player performance
- `/analyze-training [date]` - Review training sessions
- `/plan-session` - Plan training sessions
- `/review-performance [period]` - Review team performance
- `/help-coach` - Show help guide

For detailed documentation, see [chatbot/README.md](chatbot/README.md)

## Tools

- `tools/parse_timeline.py` - Parse SportEasy timeline data
- `tools/analyze_match.py` - Analyze match data
- `main.py` - Momentum analysis tool

## Testing

Run the chatbot tests:

```bash
python test_chatbot.py
```

## Requirements

```bash
pip install -r requirements.txt
```