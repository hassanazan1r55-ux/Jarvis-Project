import os
import json
import random
import datetime
import requests
import re
from dotenv import load_dotenv

load_dotenv()

class AIManager:
    def __init__(self):
        """Initialize AI Manager"""
        
        # Load config
        self.config = self.load_config()
        self.user_name = self.config.get('USER_NAME', 'Boss')
        
        # Load API key from .env
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        
        if not self.api_key:
            print("⚠️ WARNING: OPENROUTER_API_KEY not found in .env file")
        
        # Model settings
        self.model = self.config.get('OPENROUTER_MODEL', 'openai/gpt-3.5-turbo')
        self.max_tokens = self.config.get('MAX_TOKENS', 200)
        self.temperature = self.config.get('TEMPERATURE', 0.7)
        self.max_history = self.config.get('MAX_HISTORY', 10)
        
        # Conversation state
        self.conversation_history = []
        self.conversation_mode = False
        self.last_interaction = datetime.datetime.now()
        self.conversation_timeout = 30
        
        # Initialize phrases
        self.greetings = [
            f"Good Morning {self.user_name}! ☀️ How can I help you today?",
            f"Hey {self.user_name}! 👋 What's on your mind?",
            f"Hello {self.user_name}! 💪 Ready to assist you!",
            f"Good to see you {self.user_name}! 🌟 What can I do for you?",
            f"Hi there {self.user_name}! 🚀 Let's get things done!"
        ]
        
        self.farewells = [
            f"Goodbye {self.user_name}! Take care! 👋",
            "See you later boss! 🚀",
            "Shutting down. Have a great day! ✨",
            "Bye bye! Call me if you need anything! 😊",
            f"Until next time, {self.user_name}! 👋"
        ]
        
        self.thinking_phrases = [
            "Hmm, let me think about that... 🤔",
            "Interesting! Let me process that... 💭",
            "Give me a moment... ⏳",
            "Let me analyze that... 📊",
            "Processing your request... 🧠"
        ]
        
        self.acknowledgments = [
            "I understand!",
            "Got it!",
            "Makes sense!",
            "Understood!",
            "I see!"
        ]
        
        self.system_prompt = self._get_system_prompt()
        
        print(f"✅ AI Manager initialized with model: {self.model}")
        if self.api_key:
            print(f"🔑 API Key: {self.api_key[:10]}...")
    
    def load_config(self):
        """Load configuration from config.json"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ config.json not found! Using defaults.")
            return self._get_default_config()
        except json.JSONDecodeError:
            print("❌ config.json is corrupted! Using defaults.")
            return self._get_default_config()
    
    def _get_default_config(self):
        """Return default configuration"""
        return {
            "USER_NAME": "Boss",
            "OPENROUTER_MODEL": "openai/gpt-3.5-turbo",
            "MAX_TOKENS": 200,
            "TEMPERATURE": 0.7,
            "MAX_HISTORY": 10
        }
    
    def _get_system_prompt(self):
        """Generate system prompt"""
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        current_date = datetime.datetime.now().strftime('%B %d, %Y')
        
        return f"""You are JARVIS, a highly capable AI assistant for {self.user_name}. 
Current time: {current_time}
Current date: {current_date}

You are in CONTINUOUS CONVERSATION MODE. This means:
1. You can chat naturally and maintain context
2. You can ask follow-up questions
3. You can make suggestions

Your responses must be:
1. Natural and conversational
2. Short to medium length (2-4 sentences)
3. Professional yet friendly
4. Always address user as {self.user_name}

Rules:
- If user asks about time/date, provide it using current time above
- If user asks to perform an action, start response with "EXECUTE:" followed by the action
- For math problems, calculate and show result
- For general knowledge, provide accurate information
- You can ask clarifying questions
- You can offer additional help

Examples:
- User: "What's the time?" → "🕐 The current time is {current_time}"
- User: "Open Chrome" → "EXECUTE: open chrome"
- User: "Tell me a joke" → [tells joke]

Be proactive, helpful, and engaging. Make the conversation natural!"""
    
    def get_greeting(self):
        return random.choice(self.greetings)
    
    def get_farewell(self):
        return random.choice(self.farewells)
    
    def get_thinking_phrase(self):
        return random.choice(self.thinking_phrases)
    
    def get_acknowledgment(self):
        return random.choice(self.acknowledgments)
    
    def get_motivation(self):
        quotes = [
            "💪 Success is not final, failure is not fatal: it is the courage to continue that counts.",
            "🌟 The only way to do great work is to love what you do.",
            "🚀 Believe you can and you're halfway there.",
            "🔥 Your limitation—it's only your imagination.",
            "✨ Push yourself, because no one else is going to do it for you.",
            "🎯 It does not matter how slowly you go as long as you do not stop.",
            "💡 The future belongs to those who believe in the beauty of their dreams."
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
    
    def chat_with_ai(self, user_message, is_continuous=False):
        """Send message to OpenRouter API"""
        
        if not self.api_key:
            return "⚠️ API key not found. Please add OPENROUTER_API_KEY to your .env file"
        
        self.last_interaction = datetime.datetime.now()
        
        try:
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add conversation history
            for msg in self.conversation_history[-self.max_history * 2:]:
                messages.append(msg)
            
            messages.append({"role": "user", "content": user_message})
            
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
                    "top_p": 0.9
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                # Save to history
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                
                return ai_response
                
            elif response.status_code == 401:
                return "🔑 Invalid API key. Please check your OPENROUTER_API_KEY in .env file"
            elif response.status_code == 429:
                return "⏳ Rate limit exceeded. Please wait a moment and try again."
            else:
                return f"⚠️ API Error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "⏰ Request timed out. Please try again."
        except requests.exceptions.ConnectionError:
            return "🌐 Network error. Please check your internet connection."
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def process_command(self, command):
        """Process command intelligently"""
        command_lower = command.lower()
        
        # Check for conversation mode toggle
        if 'start conversation' in command_lower or 'continuous mode' in command_lower:
            self.conversation_mode = True
            return "🎯 Starting continuous conversation mode! I'll keep talking with you naturally. Say 'stop conversation' to exit."
        
        if 'stop conversation' in command_lower or 'end conversation' in command_lower:
            self.conversation_mode = False
            return "🔄 Exiting continuous conversation mode. Say 'Jarvis' to wake me up!"
        
        # Check for greetings
        if any(word in command_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good evening']):
            return self.get_greeting()
        
        # Check for farewells
        if any(word in command_lower for word in ['bye', 'goodbye', 'exit', 'quit']):
            return self.get_farewell()
        
        # Check for jokes
        if 'joke' in command_lower or 'funny' in command_lower:
            return self.tell_joke()
        
        # Check for motivation
        if 'motivate' in command_lower or 'quote' in command_lower:
            return self.get_motivation()
        
        # Check for time/date
        if 'time' in command_lower and 'date' not in command_lower:
            return f"🕐 The current time is {datetime.datetime.now().strftime('%I:%M %p')}"
        
        if 'date' in command_lower:
            return f"📅 Today is {datetime.datetime.now().strftime('%B %d, %Y')}"
        
        # Check for calculator
        if any(op in command_lower for op in ['+', '-', '*', '/', 'plus', 'minus']):
            result = self._calculate_math(command_lower)
            if result:
                return result
        
        # For everything else, use AI
        return self.chat_with_ai(command, self.conversation_mode)
    
    def _calculate_math(self, text):
        """Simple math calculator"""
        try:
            text = text.replace('plus', '+').replace('minus', '-')
            text = text.replace('times', '*').replace('divided by', '/')
            
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

# For testing
if __name__ == "__main__":
    ai = AIManager()
    print("Testing AI Manager...")
    print(ai.get_greeting())