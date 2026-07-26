import os
import json
import random
import datetime
import requests
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AIManager:
    def __init__(self):
        """Initialize AI Manager with secure API key loading"""
        
        # Load general config
        self.config = self.load_config()
        self.user_name = self.config.get('USER_NAME', 'Boss')
        
        # Load API key securely from .env
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        
        # Check if API key exists
        if not self.api_key:
            print("⚠️ WARNING: OPENROUTER_API_KEY not found in .env file")
            print("   Please create .env file with: OPENROUTER_API_KEY=your_key_here")
            print("   Get key from: https://openrouter.ai/keys")
        
        # Model configuration from config.json
        self.model = self.config.get('OPENROUTER_MODEL', 'openai/gpt-3.5-turbo')
        self.max_tokens = self.config.get('MAX_TOKENS', 200)
        self.temperature = self.config.get('TEMPERATURE', 0.7)
        
        # Conversation history
        self.conversation_history = []
        self.max_history = self.config.get('MAX_HISTORY', 6)
        
        # Initialize greeting and farewell lists
        self.greetings = [
            f"Good Morning {self.user_name}! ☀️ How can I help you today?",
            f"Hey {self.user_name}! 👋 What's on your mind?",
            f"Hello {self.user_name}! 💪 Ready to assist you!",
            f"Good to see you {self.user_name}! 🌟 What can I do for you?"
        ]
        
        self.farewells = [
            f"Goodbye {self.user_name}! Take care! 👋",
            "See you later boss! 🚀",
            "Shutting down. Have a great day! ✨",
            "Bye bye! Call me if you need anything! 😊",
            f"Until next time, {self.user_name}! 👋"
        ]
        
        # System prompt with current time
        self.system_prompt = self._get_system_prompt()
        
        # Log initialization
        print(f"✅ AI Manager initialized with model: {self.model}")
        if self.api_key:
            print(f"🔑 API Key loaded from .env (starts with: {self.api_key[:10]}...)")
    
    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ config.json not found! Using default config.")
            return self._get_default_config()
        except json.JSONDecodeError:
            print("❌ config.json is corrupted! Using default config.")
            return self._get_default_config()
    
    def _get_default_config(self):
        """Return default configuration if config.json is missing"""
        return {
            "USER_NAME": "Boss",
            "OPENROUTER_MODEL": "openai/gpt-3.5-turbo",
            "MAX_TOKENS": 200,
            "TEMPERATURE": 0.7,
            "MAX_HISTORY": 6
        }
    
    def _get_system_prompt(self):
        """Generate system prompt with current context"""
        return f"""You are JARVIS, a highly capable AI assistant for {self.user_name}. 
Current time: {datetime.datetime.now().strftime('%I:%M %p')}
Current date: {datetime.datetime.now().strftime('%B %d, %Y')}

Your responses must be:
1. Short and to the point (max 2-3 sentences)
2. Professional yet friendly
3. Extremely helpful
4. Always address user as {self.user_name}

Rules:
- If the user asks a question, answer it directly
- If they ask to perform an action, start response with "EXECUTE:" followed by the action
- For math problems, calculate and show result
- For general knowledge, provide accurate information
- For weather, ask for city name if not provided
- For time/date questions, use the current time/date provided above

Example responses:
- "EXECUTE: open chrome" (when user says "open chrome")
- "EXECUTE: search Python programming" (when user says "search Python")
- "The capital of France is Paris." (for normal question)
- "2 + 2 equals 4." (for math)
- "EXECUTE: screenshot" (when user says "take a screenshot")

Be direct, helpful, and conversational. Never say you're an AI model - just be JARVIS."""
    
    def get_greeting(self):
        """Return random greeting"""
        return random.choice(self.greetings)
    
    def get_farewell(self):
        """Return random farewell"""
        return random.choice(self.farewells)
    
    def get_motivation(self):
        """Return motivational quote"""
        quotes = [
            "💪 Success is not final, failure is not fatal: it is the courage to continue that counts.",
            "🌟 The only way to do great work is to love what you do.",
            "🚀 Believe you can and you're halfway there.",
            "🔥 Your limitation—it's only your imagination.",
            "✨ Push yourself, because no one else is going to do it for you.",
            "🎯 It does not matter how slowly you go as long as you do not stop.",
            "💡 The future belongs to those who believe in the beauty of their dreams.",
            "⚡ The only impossible journey is the one you never begin.",
            "🌟 Success is walking from failure to failure with no loss of enthusiasm."
        ]
        return random.choice(quotes)
    
    def tell_joke(self):
        """Return random tech joke"""
        jokes = [
            "😂 Why do programmers prefer dark mode? Because light attracts bugs!",
            "🤣 Why did the developer go broke? Because he used up all his cache!",
            "😄 What do you call a fake noodle? An Impasta!",
            "😅 Why was the computer cold? It left its Windows open!",
            "🤪 What did the router say to the doctor? It needs a new IP!",
            "😆 Why do Java developers wear glasses? Because they can't C#!",
            "😂 What's a computer's favorite snack? Microchips!",
            "🤣 What do you call a computer that sings? A Dell!",
            "😄 Why was the smartphone wearing glasses? It lost its contacts!"
        ]
        return random.choice(jokes)
    
    def chat_with_ai(self, user_message):
        """Send message to OpenRouter API with secure key"""
        
        # Check if API key is available
        if not self.api_key:
            return "⚠️ API key not found. Please add OPENROUTER_API_KEY to your .env file"
        
        # Check if user is asking about weather - handle specially
        if 'weather' in user_message.lower():
            return self._handle_weather(user_message)
        
        try:
            # Prepare messages with conversation history
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add conversation history (last N exchanges)
            for msg in self.conversation_history[-self.max_history * 2:]:
                messages.append(msg)
            
            messages.append({"role": "user", "content": user_message})
            
            # Make API request
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
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "top_p": 0.9,
                    "frequency_penalty": 0.3,
                    "presence_penalty": 0.3
                },
                timeout=15
            )
            
            # Handle response
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                # Save to conversation history
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                
                return ai_response
                
            elif response.status_code == 401:
                return "🔑 Invalid API key. Please check your OPENROUTER_API_KEY in .env file"
            
            elif response.status_code == 429:
                return "⏳ Rate limit exceeded. Please wait a moment and try again."
            
            else:
                error_msg = f"⚠️ API Error: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg += f" - {error_data['error'].get('message', 'Unknown error')}"
                except:
                    pass
                return error_msg
                
        except requests.exceptions.Timeout:
            return "⏰ Request timed out. Please try again."
        
        except requests.exceptions.ConnectionError:
            return "🌐 Network error. Please check your internet connection."
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _handle_weather(self, user_message):
        """Handle weather queries with city detection"""
        # Extract city from message
        city = None
        words = user_message.lower().split()
        
        # Common city names to check
        common_cities = ['karachi', 'lahore', 'islamabad', 'rawalpindi', 'faisalabad', 
                        'multan', 'hyderabad', 'gujranwala', 'peshawar', 'quetta',
                        'london', 'new york', 'dubai', 'tokyo', 'paris', 'berlin',
                        'toronto', 'sydney', 'mumbai', 'delhi', 'bangalore']
        
        for word in words:
            if word in common_cities:
                city = word.capitalize()
                break
        
        if city:
            # Return city detected
            return f"🌤️ I'll check the weather for {city}. For accurate weather data, I recommend checking Google Weather or your favorite weather app."
        else:
            return "🌤️ Please tell me which city's weather you'd like to check (e.g., 'weather in Karachi')"
    
    def process_command(self, command):
        """Process command intelligently"""
        command_lower = command.lower()
        
        # Check for greetings
        if any(word in command_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
            return self.get_greeting()
        
        # Check for farewells
        if any(word in command_lower for word in ['bye', 'goodbye', 'exit', 'quit', 'shutdown']):
            return self.get_farewell()
        
        # Check for jokes
        if 'joke' in command_lower or 'funny' in command_lower or 'laugh' in command_lower:
            return self.tell_joke()
        
        # Check for motivation
        if 'motivate' in command_lower or 'quote' in command_lower or 'inspire' in command_lower:
            return self.get_motivation()
        
        # Check for time/date (handle locally for speed)
        if 'time' in command_lower and 'date' not in command_lower:
            return f"🕐 The current time is {datetime.datetime.now().strftime('%I:%M %p')}"
        
        if 'date' in command_lower:
            return f"📅 Today is {datetime.datetime.now().strftime('%B %d, %Y')}"
        
        if 'day' in command_lower:
            return f"📅 Today is {datetime.datetime.now().strftime('%A')}"
        
        # Check for calculator (simple math)
        if any(op in command_lower for op in ['+', '-', '*', '/', 'plus', 'minus', 'times', 'divided']):
            result = self._calculate_math(command_lower)
            if result:
                return result
        
        # Check for simple knowledge questions (without using API)
        if 'who is' in command_lower or 'what is' in command_lower:
            # Let AI handle these
            pass
        
        # For everything else, use AI
        return self.chat_with_ai(command)
    
    def _calculate_math(self, text):
        """Handle simple math calculations"""
        try:
            # Clean the text
            text = text.replace('plus', '+').replace('minus', '-')
            text = text.replace('times', '*').replace('divided by', '/')
            text = text.replace('x', '*').replace('divided', '/')
            
            # Extract numbers and operator
            import re
            pattern = r'(\d+\.?\d*)\s*([+\-*/])\s*(\d+\.?\d*)'
            match = re.search(pattern, text)
            
            if match:
                num1 = float(match.group(1))
                op = match.group(2)
                num2 = float(match.group(3))
                
                if op == '+':
                    result = num1 + num2
                elif op == '-':
                    result = num1 - num2
                elif op == '*':
                    result = num1 * num2
                elif op == '/':
                    if num2 != 0:
                        result = num1 / num2
                    else:
                        return "⚠️ Cannot divide by zero"
                else:
                    return None
                
                return f"🧮 {num1} {op} {num2} = {result}"
            return None
        except:
            return None
    
    def extract_command(self, ai_response):
        """Extract executable commands from AI response"""
        if "EXECUTE:" in ai_response:
            # Split carefully
            parts = ai_response.split("EXECUTE:")
            response = parts[0].strip()
            action = parts[1].strip()
            
            return {
                'type': 'action',
                'action': action,
                'response': response
            }
        else:
            return {
                'type': 'response',
                'response': ai_response
            }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        return "🧹 Conversation history cleared"
    
    def get_history_length(self):
        """Get conversation history length"""
        return len(self.conversation_history)
    
    def get_model_info(self):
        """Get current model information"""
        return f"📊 Model: {self.model}\n🔑 API Key: {'✓' if self.api_key else '✗'}\n💬 History: {len(self.conversation_history)} messages"

# For testing
if __name__ == "__main__":
    ai = AIManager()
    print(ai.get_model_info())
    
    # Test commands
    print("\nTesting commands:")
    print(f"Greeting: {ai.get_greeting()}")
    print(f"Joke: {ai.tell_joke()}")
    print(f"Math: {ai._calculate_math('2 plus 2')}")