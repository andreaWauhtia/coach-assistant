#!/usr/bin/env python3
"""
Tests for the Coach Assistant Chatbot

Basic test suite to verify chatbot functionality.
"""

import sys
from pathlib import Path

# Add chatbot to path
sys.path.insert(0, str(Path(__file__).parent))

from chatbot import ChatbotAPI, CoachChatbot


def test_chatbot_initialization():
    """Test chatbot can be initialized."""
    bot = CoachChatbot(team_name="Test Team")
    assert bot.team_name == "Test Team"
    print("✓ Chatbot initialization test passed")


def test_api_initialization():
    """Test API can be initialized."""
    api = ChatbotAPI(team_name="Test Team")
    assert api.get_team_name() == "Test Team"
    assert api.is_active()
    print("✓ API initialization test passed")


def test_set_team_name():
    """Test team name can be set."""
    api = ChatbotAPI()
    response = api.set_team_name("New Team")
    assert api.get_team_name() == "New Team"
    assert "New Team" in response
    print("✓ Set team name test passed")


def test_help_command():
    """Test help command works."""
    api = ChatbotAPI(team_name="Test Team")
    response = api.send_message("/help-coach")
    assert "Coach Assistant" in response
    assert "/analyze-match" in response
    print("✓ Help command test passed")


def test_invalid_command():
    """Test invalid command handling."""
    api = ChatbotAPI(team_name="Test Team")
    response = api.send_message("/invalid-command")
    assert "Unknown command" in response
    print("✓ Invalid command test passed")


def test_natural_language():
    """Test natural language processing."""
    api = ChatbotAPI(team_name="Test Team")
    response = api.send_message("Hello")
    assert "Test Team" in response or "assist" in response
    print("✓ Natural language test passed")


def test_conversation_history():
    """Test conversation history tracking."""
    api = ChatbotAPI(team_name="Test Team")
    api.send_message("Hello")
    api.send_message("/help-coach")
    
    history = api.get_history()
    assert len(history) == 4  # 2 user messages + 2 bot responses
    assert history[0]['role'] == 'user'
    assert history[1]['role'] == 'assistant'
    print("✓ Conversation history test passed")


def test_clear_history():
    """Test history can be cleared."""
    api = ChatbotAPI(team_name="Test Team")
    api.send_message("Hello")
    api.clear_history()
    
    history = api.get_history()
    assert len(history) == 0
    print("✓ Clear history test passed")


def test_list_commands():
    """Test listing commands."""
    api = ChatbotAPI(team_name="Test Team")
    commands = api.list_commands()
    
    assert len(commands) == 6
    assert '/analyze-match' in commands
    assert '/scout-player' in commands
    assert '/help-coach' in commands
    print("✓ List commands test passed")


def test_command_help():
    """Test getting help for specific commands."""
    api = ChatbotAPI(team_name="Test Team")
    
    # Test with slash
    help_text = api.get_command_help('/analyze-match')
    assert 'analyze-match' in help_text.lower()
    
    # Test without slash
    help_text = api.get_command_help('scout-player')
    assert 'scout-player' in help_text.lower()
    
    print("✓ Command help test passed")


def test_session_management():
    """Test session can be ended."""
    api = ChatbotAPI(team_name="Test Team")
    assert api.is_active()
    
    api.end_session()
    assert not api.is_active()
    
    # Should raise error after ending
    try:
        api.send_message("Hello")
        assert False, "Should have raised RuntimeError"
    except RuntimeError:
        pass
    
    print("✓ Session management test passed")


def test_export_history_json():
    """Test exporting history as JSON."""
    api = ChatbotAPI(team_name="Test Team")
    api.send_message("Hello")
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        output = api.export_history(temp_path, format='json')
        assert Path(output).exists()
        
        # Check JSON is valid
        import json
        with open(output, 'r') as f:
            data = json.load(f)
        assert 'team' in data
        assert 'history' in data
        
        print("✓ Export history JSON test passed")
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_export_history_txt():
    """Test exporting history as text."""
    api = ChatbotAPI(team_name="Test Team")
    api.send_message("Hello")
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_path = f.name
    
    try:
        output = api.export_history(temp_path, format='txt')
        assert Path(output).exists()
        
        # Check text file has content
        with open(output, 'r') as f:
            content = f.read()
        assert 'Coach Assistant' in content
        assert 'Test Team' in content
        
        print("✓ Export history text test passed")
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_slash_commands():
    """Test all slash commands are registered."""
    api = ChatbotAPI(team_name="Test Team")
    
    # These should not raise errors
    api.send_message("/analyze-match 2025-01-01")
    api.send_message("/scout-player TestPlayer")
    api.send_message("/analyze-training 2025-01-01")
    api.send_message("/plan-session")
    api.send_message("/review-performance season")
    api.send_message("/help-coach")
    
    print("✓ All slash commands test passed")


def run_tests():
    """Run all tests."""
    print("Running Coach Assistant Chatbot Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_chatbot_initialization,
        test_api_initialization,
        test_set_team_name,
        test_help_command,
        test_invalid_command,
        test_natural_language,
        test_conversation_history,
        test_clear_history,
        test_list_commands,
        test_command_help,
        test_session_management,
        test_export_history_json,
        test_export_history_txt,
        test_slash_commands,
    ]
    
    failed = []
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed.append(test.__name__)
    
    print()
    print("=" * 60)
    
    if failed:
        print(f"FAILED: {len(failed)} tests failed")
        for name in failed:
            print(f"  - {name}")
        return 1
    else:
        print(f"SUCCESS: All {len(tests)} tests passed! ✓")
        return 0


if __name__ == "__main__":
    sys.exit(run_tests())
