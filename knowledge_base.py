# Static Knowledge Base (Hash Map)

STATIC_RESPONSES = {
    "hello": "Hello! I am your TravelBot assistant. How can I help you today?",
    "hi": "Hi there! Looking for a vacation in Sri Lanka? I can help with packages, hotels, and travel advice.",
    "hey": "Hey! Ready to explore beautiful destinations? Ask me about tours or accommodation.",
    "thank you": "You're very welcome! I'm here to make your travel planning easy.",
    "thanks": "No problem! Let me know if you have more questions.",
    "good morning": "Good morning! It's a great day to plan a journey.",
    "good evening": "Good evening! Hope you're having a wonderful time.",
    "bye": "Goodbye! Have a safe and pleasant journey.",
    "goodbye": "Farewell! Hope to see you again soon.",
    "what can you do": "I can help you find holiday packages, search for hotels in Sri Lanka, give details about destinations, and even learn from our conversations!",
    "who are you": "I am TravelBot, an AI-powered travel assistant specialized in Sri Lanka tourism.",
    "help": "You can ask things like: 'Show me holiday packages', 'Find hotels in Colombo', 'Tell me about Ella', or just chat with me!"
}

def get_static_response(user_input):
    """Checks for an exact or keyword match in the static KB."""
    user_input = user_input.lower().strip()
    
    # Check for direct matches
    if user_input in STATIC_RESPONSES:
        return STATIC_RESPONSES[user_input]
    
    # Check if any key is inside the user input
    for key in STATIC_RESPONSES:
        if key in user_input:
            # For short keys like 'hi', make sure it's a separate word
            if len(key) <= 3:
                words = user_input.split()
                if key in words:
                    return STATIC_RESPONSES[key]
            else:
                return STATIC_RESPONSES[key]
                
    return None
