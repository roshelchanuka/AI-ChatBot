import os
from openai import OpenAI
from dotenv import load_dotenv
from database import query_packages, query_hotels, query_destinations
from knowledge_base import get_static_response
from ml_learner import get_learned_match
import re

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

import wikipediaapi
import requests

class InferenceEngine:
    def __init__(self):
        self.system_prompt = """You are TravelBot, a professional and friendly travel consultant for Sri Lanka.
        You provide detailed, helpful advice about tours, hotels, and destinations in Sri Lanka.
        If a user asks for packages or hotels, remind them you can search the database.
        Keep responses concise and inviting."""
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
            return f"I couldn't find any packages in '{dest_name}'. Try another location!", "Dynamic DB"

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
            return f"Sorry, I don't have any hotels listed in '{loc_name}' yet.", "Dynamic DB"

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
                
            return f"I don't have details on '{dest_name}' in my records or online.", "Dynamic DB"

        # Tier 3: OpenAI GPT Fallback
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7
            )
            return response.choices.message.content, "AI GPT"
        except Exception as e:
            return f"I'm having trouble connecting to my AI brain right now. Error: {str(e)}", "Error"

# Singleton
engine = InferenceEngine()

def get_bot_response(user_input):
    return engine.process_query(user_input)
