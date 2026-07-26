import random
import datetime
import json
import requests
import re

class AIManager:
    def __init__(self):
        self.config = self.load_config()
        self.user_name = self.config.get('USER_NAME', 'Boss')
        self.api_key = self.config.get('OPENROUTER_API_KEY', '')
        self.model = self.config.get('OPENROUTER_MODEL', 'openai/gpt-3.5-turbo')
        self.conversation_history = []
        self.system_prompt = self.get_system_prompt()
    
    def load_config(self):
        with open('config.json', 'r') as f:
            return json.load(f)
    
    def get_system_prompt(self):
        return f"""You are JARVIS, an AI assistant for {self.user_name}. Your responses should be:
1. Concise and helpful
2. Professional but friendly
3. Direct and to the point
4. Always address the user as {self.user_name}

Current date and time: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}

If the user asks about:
- Time/Date: Provide current time/date
- Weather: Ask for city name
- Math: Calculate and explain
- General knowledge: Provide accurate information
- Commands: Reply with "EXECUTE:" followed by the action

Keep responses under 2 sentences unless asked for details."""
    
    def get_greeting(self):
        hour = datetime.datetime.now().hour
        if 0 <= hour < 12:
            return f"Good Morning {self.user_name}! ☀️ How can I assist you today?"
        elif 12 <= hour < 18:
            return f"Good Afternoon {self.user_name}! 🌤️ Ready to help you!"
        else:
            return f"Good Evening {self.user_name}! 🌙 How may I be of service?"
    
    def get_farewell(self):
        farewells = [
            f"Goodbye {self.user_name}! Take care! 👋",
            "Shutting down. Have a great day! ✨",
            "Bye bye! Don't forget to call me back! 😊",
            "See you later, boss! 🚀"
        ]
        return random.choice(farewells)
    
    def chat_with_ai(self, user_message):
        """Send message to OpenRouter API"""
        if not self.api_key:
            return "⚠️ OpenRouter API key not configured. Please add your API key in config.json"
        
        try:
            # Prepare messages
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add conversation history (last 5 exchanges)
            for msg in self.conversation_history[-10:]:
                messages.append(msg)
            
            messages.append({"role": "user", "content": user_message})
            
            # API Call
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "JARVIS Assistant"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 200
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                # Save to conversation history
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                
                return ai_response
            else:
                return f"⚠️ API Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "⏰ Request timed out. Please try again."
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def process_command(self, command):
        """Process command with AI and extract actions"""
        command_lower = command.lower()
        
        # Check for special commands first (don't send to AI)
        special_commands = {
            'hello': self.get_greeting,
            'hi': self.get_greeting,
            'hey': self.get_greeting,
            'bye': self.get_farewell,
            'goodbye': self.get_farewell,
            'exit': self.get_farewell,
            'quit': self.get_farewell
        }
        
        for key, func in special_commands.items():
            if key in command_lower:
                return func()
        
        # Send to AI for all other commands
        return self.chat_with_ai(command)
    
    def extract_command(self, ai_response):
        """Extract executable commands from AI response"""
        # Check if AI wants to execute a command
        if "EXECUTE:" in ai_response:
            action = ai_response.split("EXECUTE:")[1].strip()
            return {
                'type': 'action',
                'action': action,
                'response': ai_response.replace("EXECUTE:", "").strip()
            }
        else:
            return {
                'type': 'response',
                'response': ai_response
            }
    
    def get_motivation(self):
        quotes = [
            "💪 Success is not final, failure is not fatal: it is the courage to continue that counts.",
            "🌟 The only way to do great work is to love what you do.",
            "🚀 Believe you can and you're halfway there.",
            "🔥 It does not matter how slowly you go as long as you do not stop.",
            "✨ The future belongs to those who believe in the beauty of their dreams.",
            "🎯 Your limitation—it's only your imagination.",
            "⚡ Push yourself, because no one else is going to do it for you."
        ]
        return random.choice(quotes)
    
    def tell_joke(self):
        jokes = [
            "😂 Why do programmers prefer dark mode? Because light attracts bugs!",
            "🤣 Why did the developer go broke? Because he used up all his cache!",
            "😄 What do you call a fake noodle? An Impasta!",
            "😅 Why was the computer cold? It left its Windows open!",
            "🤪 What did the router say to the doctor? It needs a new IP!",
            "😆 Why do Java developers wear glasses? Because they can't C#!"
        ]
        return random.choice(jokes)