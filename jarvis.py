import sys
import os
import json
import time
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from system import SystemManager
from browser import BrowserManager
from ai import AIManager

try:
    import pyttsx3
    VOICE_AVAILABLE = True
except:
    VOICE_AVAILABLE = False

try:
    import speech_recognition as sr
    MIC_AVAILABLE = True
except:
    MIC_AVAILABLE = False

class Jarvis:
    def __init__(self):
        print("🚀 Initializing JARVIS...")
        
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        
        self.user_name = self.config.get('USER_NAME', 'Boss')
        
        self.system = SystemManager()
        self.browser = BrowserManager()
        self.ai = AIManager()
        
        self.engine = None
        if VOICE_AVAILABLE:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.config.get('VOICE_SPEED', 170))
            self.engine.setProperty('volume', self.config.get('VOICE_VOLUME', 0.9))
        
        self.recognizer = sr.Recognizer() if MIC_AVAILABLE else None
        
        self.running = True
        self.log_file = 'logs/history.log'
        os.makedirs('logs', exist_ok=True)
        
        self.log("JARVIS Started")
        print("✅ JARVIS is ready!")
        
        # Check API key
        if not self.config.get('OPENROUTER_API_KEY'):
            print("⚠️ WARNING: OpenRouter API key not found in config.json")
            print("   Add your API key to enable AI features")
            print("   Get key from: https://openrouter.ai/keys\n")
    
    def speak(self, text):
        print(f"🤖 JARVIS: {text}")
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
    
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def greet(self):
        greeting = self.ai.get_greeting()
        self.speak(greeting)
    
    def execute_system_action(self, action):
        """Execute system actions from AI"""
        action_lower = action.lower()
        
        # Time/Date
        if 'time' in action_lower:
            time_str = self.system.get_time()
            self.speak(f"The time is {time_str}")
            return True
        elif 'date' in action_lower:
            date_str = self.system.get_date()
            self.speak(f"Today is {date_str}")
            return True
        
        # Open apps
        elif 'open' in action_lower:
            for app in ['notepad', 'calculator', 'chrome', 'word', 'excel', 'spotify', 'vscode', 'paint', 'cmd']:
                if app in action_lower:
                    result = self.system.open_app(app)
                    self.speak(result)
                    return True
        
        # Close apps
        elif 'close' in action_lower or 'kill' in action_lower:
            for app in ['notepad', 'chrome', 'word', 'excel', 'spotify']:
                if app in action_lower:
                    result = self.system.close_app(app)
                    self.speak(result)
                    return True
        
        # Screenshot
        elif 'screenshot' in action_lower:
            result = self.system.take_screenshot()
            self.speak(result)
            return True
        
        # System status
        elif 'status' in action_lower or 'battery' in action_lower:
            status = self.system.get_system_status()
            bat = status['battery']
            self.speak(f"Battery: {bat['percent']}%, {'Charging' if bat['plugged'] else 'On Battery'}")
            self.speak(f"CPU: {status['cpu']}%, RAM: {status['ram']}%")
            return True
        
        # Shutdown/Restart/Lock
        elif 'shutdown' in action_lower:
            self.speak("Shutting down system in 5 seconds. Goodbye!")
            self.system.shutdown_system()
            self.running = False
            return True
        elif 'restart' in action_lower:
            self.speak("Restarting system in 5 seconds")
            self.system.restart_system()
            self.running = False
            return True
        elif 'lock' in action_lower:
            result = self.system.lock_system()
            self.speak(result)
            return True
        
        # Search
        elif 'search' in action_lower:
            query = action_lower.replace('search', '').strip()
            if query:
                result = self.browser.search_google(query)
                self.speak(result)
                return True
        
        # YouTube
        elif 'youtube' in action_lower:
            query = action_lower.replace('youtube', '').strip()
            if query:
                result = self.browser.search_youtube(query)
                self.speak(result)
                return True
        
        # Open website
        elif 'website' in action_lower or 'open' in action_lower:
            for site in ['google', 'youtube', 'github', 'gmail', 'stackoverflow']:
                if site in action_lower:
                    result = self.browser.open_website(site)
                    self.speak(result)
                    return True
        
        return False
    
    def process_command(self, command):
        if not command:
            return
        
        self.log(f"Command: {command}")
        
        # First check if it's a direct command
        direct_handled = self.execute_system_action(command)
        if direct_handled:
            return
        
        # If not direct, send to AI
        ai_response = self.ai.process_command(command)
        
        # Check if AI wants to execute an action
        extracted = self.ai.extract_command(ai_response)
        
        if extracted['type'] == 'action':
            # AI wants to execute something
            self.speak(extracted['response'])
            self.execute_system_action(extracted['action'])
        else:
            # AI just responds
            self.speak(extracted['response'])
    
    def listen_voice(self):
        if not MIC_AVAILABLE:
            self.speak("Microphone not available")
            return None
        
        with sr.Microphone() as source:
            print("🎤 Listening...")
            self.speak("Listening...")
            self.recognizer.pause_threshold = 1
            self.recognizer.energy_threshold = 300
            
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("🔄 Processing...")
                command = self.recognizer.recognize_google(audio, language='en-US')
                print(f"📝 You said: {command}")
                return command.lower()
            except sr.WaitTimeoutError:
                self.speak("No voice detected")
                return None
            except sr.UnknownValueError:
                self.speak("Sorry, I didn't catch that")
                return None
            except sr.RequestError:
                self.speak("Network error")
                return None
    
    def show_commands(self):
        commands = """
        📌 AVAILABLE COMMANDS:
        ================================
        🧠 Now with AI!
        - Just tell me anything naturally
        - I'll understand and respond
        
        🕐 System:
          - time, date, battery, status
          - screenshot, lock, shutdown, restart
        
        📂 Apps:
          - open [notepad/chrome/word/excel/spotify/vscode/paint/cmd]
          - close [notepad/chrome/word/excel/spotify]
        
        🌐 Web:
          - search [query]
          - youtube [query]
          - open website [name]
        
        🤖 AI:
          - Any question! Just ask
          - motivate, quote, joke
          - weather [city]
          - math calculations
          - General knowledge
        
        ================================
        """
        print(commands)
        self.speak("Commands displayed in console")
    
    def run(self):
        self.greet()
        
        while self.running:
            print("\n" + "="*50)
            print("📋 JARVIS MENU")
            print("="*50)
            print("1. 🖱️ Type Command")
            print("2. 🎤 Voice Command")
            print("3. 📝 Show Commands")
            print("4. 💬 AI Chat Mode")
            print("5. ❌ Exit")
            print("="*50)
            
            choice = input("Select option (1-5): ").strip()
            
            if choice == "1":
                command = input("💬 Type your command: ").strip()
                if command:
                    self.process_command(command)
            
            elif choice == "2":
                command = self.listen_voice()
                if command:
                    self.process_command(command)
            
            elif choice == "3":
                self.show_commands()
            
            elif choice == "4":
                self.speak("AI chat mode. Ask me anything!")
                while True:
                    user_input = input("🧑 You: ").strip()
                    if user_input.lower() in ['exit', 'quit', 'back']:
                        self.speak("Exiting chat mode")
                        break
                    response = self.ai.chat_with_ai(user_input)
                    print(f"🤖 JARVIS: {response}")
                    self.speak(response)
            
            elif choice == "5":
                self.speak(self.ai.get_farewell())
                self.log("JARVIS Stopped")
                self.running = False
                break
            
            else:
                self.speak("Invalid option, please try again")

if __name__ == "__main__":
    try:
        jarvis = Jarvis()
        jarvis.run()
    except KeyboardInterrupt:
        print("\n⚠️ JARVIS interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")