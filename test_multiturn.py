"""
Test script for multi-turn conversation functionality
This demonstrates how the chatbot maintains conversation context across multiple messages.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"  # Change this if your server runs on a different port
SESSION_ID = "test-session-123"  # Unique identifier for this conversation

def send_message(message: str, session_id: str = SESSION_ID):
    """Send a message to the chatbot and get a response."""
    url = f"{BASE_URL}/chat"
    payload = {
        "message": message,
        "session_id": session_id
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "No response received")
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"


def clear_history(session_id: str = SESSION_ID):
    """Clear the conversation history for a session."""
    url = f"{BASE_URL}/clear-history"
    params = {"session_id": session_id}
    
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        result = response.json()
        return result.get("message", "History cleared")
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"


def test_multi_turn_conversation():
    """Test multi-turn conversation with context retention."""
    print("=" * 60)
    print("Testing Multi-Turn Conversation")
    print("=" * 60)
    
    # Test 1: First message
    print("\n[User]: What projects has Clay worked on?")
    response1 = send_message("What projects has Clay worked on?")
    print(f"[ClayBot]: {response1}\n")
    
    # Test 2: Follow-up question (should remember context)
    print("[User]: Can you tell me more about the first one?")
    response2 = send_message("Can you tell me more about the first one?")
    print(f"[ClayBot]: {response2}\n")
    
    # Test 3: Another follow-up
    print("[User]: What technologies did he use for that project?")
    response3 = send_message("What technologies did he use for that project?")
    print(f"[ClayBot]: {response3}\n")
    
    # Test 4: Change topic
    print("[User]: What are Clay's skills?")
    response4 = send_message("What are Clay's skills?")
    print(f"[ClayBot]: {response4}\n")
    
    # Test 5: Reference previous topic
    print("[User]: How do those skills relate to the projects we discussed earlier?")
    response5 = send_message("How do those skills relate to the projects we discussed earlier?")
    print(f"[ClayBot]: {response5}\n")
    
    print("=" * 60)
    print("Clearing conversation history...")
    print("=" * 60)
    clear_result = clear_history()
    print(f"{clear_result}\n")
    
    # Test 6: After clearing history (should not remember previous context)
    print("[User]: What was the first project we talked about?")
    response6 = send_message("What was the first project we talked about?")
    print(f"[ClayBot]: {response6}\n")
    
    print("=" * 60)
    print("Multi-turn conversation test completed!")
    print("=" * 60)


def test_multiple_sessions():
    """Test that different sessions maintain separate conversation histories."""
    print("\n" + "=" * 60)
    print("Testing Multiple Sessions")
    print("=" * 60)
    
    session1 = "session-1"
    session2 = "session-2"
    
    # Session 1: Talk about projects
    print(f"\n[Session 1 - User]: Tell me about Clay's AI projects")
    response1 = send_message("Tell me about Clay's AI projects", session1)
    print(f"[Session 1 - ClayBot]: {response1[:100]}...")
    
    # Session 2: Talk about skills
    print(f"\n[Session 2 - User]: What programming languages does Clay know?")
    response2 = send_message("What programming languages does Clay know?", session2)
    print(f"[Session 2 - ClayBot]: {response2[:100]}...")
    
    # Session 1: Follow-up on projects
    print(f"\n[Session 1 - User]: Which one is your favorite?")
    response3 = send_message("Which one is your favorite?", session1)
    print(f"[Session 1 - ClayBot]: {response3[:100]}...")
    
    # Session 2: Follow-up on skills
    print(f"\n[Session 2 - User]: Is he proficient in Python?")
    response4 = send_message("Is he proficient in Python?", session2)
    print(f"[Session 2 - ClayBot]: {response4[:100]}...")
    
    # Clear both sessions
    print("\nClearing both sessions...")
    clear_history(session1)
    clear_history(session2)
    
    print("=" * 60)
    print("Multiple sessions test completed!")
    print("=" * 60)


if __name__ == "__main__":
    print("\n🤖 ClayBot Multi-Turn Conversation Test\n")
    
    # Test 1: Multi-turn conversation
    test_multi_turn_conversation()
    
    # Test 2: Multiple sessions
    test_multiple_sessions()
    
    print("\n✅ All tests completed!\n")
