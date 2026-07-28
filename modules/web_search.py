import os
import requests
from dotenv import load_dotenv

load_dotenv()

class WebSearch:
    def __init__(self):
        self.api_key = os.getenv('SERPAPI_API_KEY')
        if not self.api_key:
            print("⚠️ SERPAPI_API_KEY not found in .env. Internet features disabled.")
    
    def search(self, query):
        """Search Google and return top results."""
        if not self.api_key:
            return "API key missing. Please add SERPAPI_API_KEY to .env"
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "num": 3
        }
        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=10)
            data = response.json()
            results = data.get("organic_results", [])
            if results:
                snippets = [f"{r.get('title', '')}: {r.get('snippet', '')}" for r in results[:3]]
                return "\n".join(snippets)
            else:
                return "No results found."
        except Exception as e:
            return f"Search error: {str(e)}"
    
    def get_weather(self, city="Karachi"):
        """Get weather for a city."""
        if not self.api_key:
            return "API key missing."
        params = {
            "q": f"weather {city}",
            "api_key": self.api_key,
            "engine": "google"
        }
        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=10)
            data = response.json()
            weather = data.get("weather_results", {})
            if weather:
                temp = weather.get("temperature", "N/A")
                desc = weather.get("description", "N/A")
                return f"Weather in {city}: {temp}, {desc}"
            else:
                return f"Could not fetch weather for {city}."
        except Exception as e:
            return f"Weather error: {str(e)}"
    
    def get_news(self, topic="latest"):
        """Get news headlines on a topic."""
        if not self.api_key:
            return "API key missing."
        params = {
            "q": topic,
            "api_key": self.api_key,
            "engine": "google_news",
            "num": 3
        }
        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=10)
            data = response.json()
            news = data.get("news_results", [])
            if news:
                headlines = [f"• {n.get('title', '')}" for n in news[:3]]
                return "\n".join(headlines)
            else:
                return "No news found."
        except Exception as e:
            return f"News error: {str(e)}"