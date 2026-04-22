
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- Validate API Key BEFORE starting ---
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print(" ERROR: OPENAI_API_KEY not found in .env file")
    print("Please create a .env file with: OPENAI_API_KEY=your-key-here")
    exit(1)  # Stop the program

client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = "You are a helpful, friendly assistant."
conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]

def chat(user_message):
    """Send message to AI with error handling."""
    conversation_history.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history,
            temperature=0.7,
            max_tokens=500
        )
        ai_reply = response.choices.message.content
        conversation_history.append({"role": "assistant", "content": ai_reply})
        return ai_reply
    
    except Exception as e:
        # Remove the failed user message from history
        conversation_history.pop()
        
        error_msg = str(e)
        
        if "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
            return " Error: Invalid API key. Check your .env file."
        elif "rate_limit" in error_msg.lower():
            return " Error: Too many requests. Please wait a moment and try again."
        elif "insufficient_quota" in error_msg.lower():
            return " Error: API quota exceeded. Check your OpenAI billing."
        elif "connection" in error_msg.lower():
            return " Error: No internet connection. Please check your network."
        else:
            return f"Unexpected error: {error_msg}"

print("Chatbot Ready! (Type 'quit' to exit)\n")

while True:
    user_input = input("You: ").strip()
    
    if not user_input:
        continue
    if user_input.lower() in {"quit", "exit"}:
        print("AI: Goodbye!")
        break
    if user_input.lower() == "reset":
        conversation_history.clear()
        conversation_history.append({"role": "system", "content": SYSTEM_PROMPT})
        print("Chat reset.\n")
        continue
    
    reply = chat(user_input)
    print(f"AI: {reply}\n")
