import os
from openai import OpenAI
from dotenv import load_dotenv
from database import query_packages, query_hotels, query_destinations
from knowledge_base import get_static_response
from ml_learner import get_learned_match
import re

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("WARNING: OPENAI_API_KEY is missing!")
    client = None
else:
    client = OpenAI(api_key=api_key)

import wikipediaapi
import requests
from duckduckgo_search import DDGS

class InferenceEngine:
    def __init__(self):
        self.system_prompt = """You are TravelBot, a professional and friendly travel consultant. 
        While you specialize in Sri Lanka, you have full access to the internet to answer ANY question about travel, history, weather, or news worldwide.
        
        CRITICAL INSTRUCTIONS:
        1. If a user asks for information NOT in your local database (like hotels in foreign countries, global history, or current events), 
           ALWAYS use the 'web_search' tool immediately.
        2. Never say "I don't have that in my database" or "I only store data". Instead, just search Google/Internet and provide the answer.
        3. Make your responses inviting, thorough, and professional."""
        # Initialize Wikipedia
        self.wiki = wikipediaapi.Wikipedia(
            user_agent="TravelBot/1.0 (contact@example.com)",
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )

    def get_weather(self, city):
        """Fetches live weather from wttr.in (Free API)."""
        try:
            # Use wttr.in for easy, key-less weather
            url = f"https://wttr.in/{city}?format=%C+%t"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return f"The current weather in {city.capitalize()} is: **{response.text}**"
        except:
            pass
        return None

    def search_wikipedia(self, query):
        """Searches Wikipedia for live facts."""
        try:
            page = self.wiki.page(query)
            if page.exists():
                return page.summary[:1200] + "..."
        except:
            pass
        return None

    def search_web(self, query):
        """Performs a robust web search using DuckDuckGo."""
        try:
            with DDGS() as ddgs:
                # Try search
                results = list(ddgs.text(query, max_results=8))
                if not results:
                    # Retry with a slightly modified query if first one fails
                    results = list(ddgs.text(f"travel information {query}", max_results=5))
                
                if results:
                    search_results = "\n\n".join([f"Title: {r.get('title')}\nSnippet: {r.get('body')}\nSource: {r.get('href')}" for r in results])
                    return search_results
        except Exception as e:
            print(f"Search error: {e}")
        return None

    def get_intent(self, text):
        """Simple keyword-based intent detection for database routing."""
        text = text.lower()
        if any(word in text for word in ["weather", "temperature", "climate in"]):
            return "query_weather"
        if any(word in text for word in ["package", "tour", "holiday", "plan"]):
            return "query_packages"
        if any(word in text for word in ["hotel", "stay", "accommodation", "resort"]):
            return "query_hotels"
        if any(word in text for word in ["tell me about", "what is", "info on", "history of"]):
            return "query_destinations"
        return "general"

    def process_query(self, user_input):
        """Main 4-tier inference logic (now with Web Search)."""
        
        # Tier 1: Static Knowledge Base
        static_resp = get_static_response(user_input)
        if static_resp:
            return static_resp, "Static KB"

        # Tier 2: ML Learned Responses
        learned_resp = get_learned_match(user_input)
        if learned_resp:
            return learned_resp, "ML Learned"

        # Tier 3: Dynamic Database Queries
        intent = self.get_intent(user_input)
        
        if intent == "query_weather":
            city = user_input.split()[-1] # Usually the last word
            weather_info = self.get_weather(city)
            if weather_info:
                return weather_info, "Live Web Search"

        if intent == "query_packages":
            # Extract destination (e.g., 'packages in Sigiriya')
            dest_match = re.search(r'in ([\w\s]+)', user_input, re.IGNORECASE)
            dest_name = dest_match.group(1).strip() if dest_match else None
            
            packages = query_packages(dest_name)
            if packages:
                resp = f"Here are holiday packages{' in ' + dest_name if dest_name else ''}:\n\n"
                for p in packages:
                    resp += f"🏝️ **{p[1]}** ({p[3]})\n💰 Price: ${p[4]}\n📝 {p[5]}\n\n"
                return resp, "Dynamic DB"
            # No return here -> fall through to AI if DB is empty

        if intent == "query_hotels":
            # Extract location (e.g., 'hotels in Colombo')
            loc_match = re.search(r'in ([\w\s]+)', user_input, re.IGNORECASE)
            loc_name = loc_match.group(1).strip() if loc_match else None
            
            hotels = query_hotels(loc_name)
            if hotels:
                resp = f"I found these hotels{' in ' + loc_name if loc_name else ''}:\n\n"
                for h in hotels:
                    resp += f"🏨 **{h[1]}** ({h[3]} Stars)\n📍 Location: {h[2]}\n💵 Rate: ${h[4]}/night\n✨ {h[5]}\n\n"
                return resp, "Dynamic DB"
            # No return here -> fall through to AI if DB is empty

        if intent == "query_destinations":
            # Extract destination name (e.g., 'tell me about Ella')
            dest_match = re.search(r'(about|on|history of) ([\w\s]+)', user_input, re.IGNORECASE)
            dest_name = dest_match.group(2).strip().capitalize() if dest_match else user_input.split()[-1].capitalize()
            
            # Try DB first
            dest = query_destinations(dest_name)
            if dest:
                d = dest[0]
                return f"📍 **{d[1]}**\n🌟 Attractions: {d[2]}\n☁️ Climate: {d[3]}\n🗓️ Best Time: {d[4]}", "Dynamic DB"
            
            # Try Wikipedia next (Live Search)
            wiki_summary = self.search_wikipedia(dest_name)
            if wiki_summary:
                return f"🌐 **{dest_name} (from Wikipedia)**\n\n{wiki_summary}", "Live Web Search"
                
            # fall through to Tier 4

        # Tier 4: OpenAI GPT with Web Search Tool
        try:
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "description": "Search the internet for up-to-date information, news, travel details, historical facts, or anything else NOT in the local database. Use this for Google-style searches.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "The specific search query for the internet"}
                            },
                            "required": ["query"]
                        }
                    }
                }
            ]

            messages = [
                {"role": "system", "content": self.system_prompt + "\nYou can use the web_search tool if you need information you don't have."},
                {"role": "user", "content": user_input}
            ]

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                temperature=0.7
            )

            assistant_message = response.choices[0].message
            
            # Check if tool call is needed
            if assistant_message.tool_calls:
                tool_call = assistant_message.tool_calls[0]
                if tool_call.function.name == "web_search":
                    import json
                    args = json.loads(tool_call.function.arguments)
                    search_query = args.get("query")
                    
                    search_content = self.search_web(search_query)
                    
                    if search_content:
                        # Add tool response to history
                        messages.append(assistant_message)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": "web_search",
                            "content": search_content
                        })
                        
                        # Get final response
                        final_response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=messages,
                            temperature=0.7
                        )
                        return final_response.choices[0].message.content, "Web Search"
                    else:
                        return "I tried to search the web but couldn't find anything relevant.", "Web Search"

            return assistant_message.content, "AI GPT"
        except Exception as e:
            return f"I'm having trouble connecting to my AI brain or search tool. Error: {str(e)}", "Error"

# Singleton
engine = InferenceEngine()

def get_bot_response(user_input):
    return engine.process_query(user_input)
