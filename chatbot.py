
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print(" AI Chatbot is ready! Type 'quit' to exit.\n")

# Keep chatting until the user types 'quit'
while True:
    # Get input from the user
    user_input = input("You: ")
    
    # Check if user wants to quit
    if user_input.strip().lower() in {"quit", "exit", "bye"}:
        print("AI: Goodbye! Have a great day!")
        break
    
    # Skip empty messages
    if not user_input.strip():
        continue
    
    # Send message to AI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
        max_tokens=300
    )
    
    # Print the AI's reply
    reply = response.choices.message.content
    print(f"AI: {reply}\n")

