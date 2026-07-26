import webbrowser
import json

class BrowserManager:
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        with open('config.json', 'r') as f:
            return json.load(f)
    
    def search_google(self, query):
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searching Google for: {query}"
    
    def search_youtube(self, query):
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return f"Searching YouTube for: {query}"
    
    def open_website(self, site_name):
        websites = self.config.get('WEBSITES', {})
        if site_name in websites:
            webbrowser.open(websites[site_name])
            return f"Opening {site_name}"
        else:
            webbrowser.open(f"https://www.{site_name}.com")
            return f"Opening {site_name}.com"
    
    def search_wikipedia(self, query):
        webbrowser.open(f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}")
        return f"Searching Wikipedia for: {query}"