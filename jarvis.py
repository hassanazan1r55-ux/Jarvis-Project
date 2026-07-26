import sys
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.system import SystemManager
from modules.browser import BrowserManager
from modules.ai import AIManager

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
        print("""
    ╔═══════════════════════════════════════════════╗
    ║     🚀 JARVIS AI ASSISTANT v7.2              ║
    ║     IMPROVED COMMAND PARSING                 ║
    ║     Say "AI" + command                      ║
    ╚═══════════════════════════════════════════════╝
        """)
        
        if not os.path.exists('.env'):
            print("⚠️ WARNING: .env file not found!\n")
        
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except:
            self.config = self._create_default_config()
        
        self.user_name = self.config.get('USER_NAME', 'Boss')
        
        # ============================================
        # 🔥 WAKE WORD - CHANGE HERE!
        # ============================================
        self.WAKE_WORD = "ai"  # Options: "ai", "jar", "jay", "hey"
        # ============================================
        
        self.conversation_active = False
        self.processing = False
        
        self.system = SystemManager()
        self.browser = BrowserManager()
        self.ai = AIManager()
        
        # Voice engine
        self.engine = None
        if VOICE_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 170)
                self.engine.setProperty('volume', 0.9)
            except:
                pass
        
        # Microphone setup
        self.recognizer = None
        self.microphone = None
        
        if MIC_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.recognizer.energy_threshold = 4000
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 0.8
                
                self.microphone = sr.Microphone()
                
                print("🎤 Calibrating microphone...")
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=2)
                
                print(f"✅ Microphone ready!")
                print(f"   Energy threshold: {self.recognizer.energy_threshold:.0f}")
                print(f"   Wake Word: '{self.WAKE_WORD}'")
                
            except Exception as e:
                print(f"⚠️ Microphone error: {e}")
                self.recognizer = None
        
        self.running = True
        self.log_file = 'logs/history.log'
        os.makedirs('logs', exist_ok=True)
        
        self.log("JARVIS Started")
        print("\n✅ JARVIS is ready!")
        print(f"🎤 Say '{self.WAKE_WORD}' + command")
        print(f"💡 Examples: '{self.WAKE_WORD} time', '{self.WAKE_WORD} open chrome'")
        print("="*50)
    
    def _create_default_config(self):
        default_config = {
            "USER_NAME": "Boss",
            "VOICE_SPEED": 170,
            "VOICE_VOLUME": 0.9,
            "VOICE_GENDER": "male",
            "OPENROUTER_MODEL": "openai/gpt-3.5-turbo",
            "MAX_TOKENS": 200,
            "TEMPERATURE": 0.7,
            "MAX_HISTORY": 10,
            "WAKE_WORD": "ai",
            "APPS": {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe",
                "word": "winword.exe",
                "excel": "excel.exe",
                "spotify": "spotify.exe",
                "vscode": "code.exe",
                "paint": "mspaint.exe",
                "cmd": "cmd.exe"
            },
            "WEBSITES": {
                "google": "https://www.google.com",
                "youtube": "https://www.youtube.com",
                "github": "https://www.github.com",
                "gmail": "https://mail.google.com"
            }
        }
        with open('config.json', 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config
    
    def speak(self, text):
        print(f"🤖 JARVIS: {text}")
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except:
                pass
    
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
        except:
            pass
    
    def greet(self):
        try:
            greeting = self.ai.get_greeting()
            self.speak(greeting)
            self.speak(f"Say {self.WAKE_WORD} and your command!")
        except:
            self.speak("Hello! I'm JARVIS.")
    
    def execute_action(self, action):
        if not action:
            return False
        
        action_lower = action.lower()
        self.log(f"Executing: {action_lower}")
        
        # ============================================
        # 🔥 IMPROVED COMMAND PARSING
        # ============================================
        
        # Time
        if 'time' in action_lower and 'date' not in action_lower:
            time_str = self.system.get_time()
            self.speak(f"The time is {time_str}")
            return True
        
        # Date
        elif 'date' in action_lower:
            date_str = self.system.get_date()
            self.speak(f"Today is {date_str}")
            return True
        
        # Open apps
        elif 'open' in action_lower:
            # Check each app
            app_found = False
            for app in ['notepad', 'calculator', 'chrome', 'word', 'excel', 'spotify', 'vscode', 'paint', 'cmd']:
                if app in action_lower:
                    result = self.system.open_app(app)
                    self.speak(result)
                    app_found = True
                    break
            
            if not app_found:
                # Try to extract app name
                words = action_lower.split()
                for word in words:
                    if word not in ['open', 'please']:
                        self.speak(f"I don't know how to open {word}")
                        break
            return True
        
        # Close apps
        elif 'close' in action_lower or 'kill' in action_lower:
            app_found = False
            for app in ['notepad', 'chrome', 'word', 'excel', 'spotify', 'vscode']:
                if app in action_lower:
                    result = self.system.close_app(app)
                    self.speak(result)
                    app_found = True
                    break
            
            if not app_found:
                self.speak("I don't know which app to close")
            return True
        
        # Screenshot
        elif 'screenshot' in action_lower or 'capture' in action_lower:
            result = self.system.take_screenshot()
            self.speak(result)
            return True
        
        # System status
        elif 'status' in action_lower or 'battery' in action_lower:
            try:
                status = self.system.get_system_status()
                bat = status['battery']
                self.speak(f"Battery {bat['percent']}%, {'charging' if bat['plugged'] else 'on battery'}")
            except:
                self.speak("Can't get status")
            return True
        
        # Google Search
        elif 'search' in action_lower:
            # Extract search query
            query = action_lower.replace('search', '').strip()
            # Remove common words
            for word in ['for', 'about', 'please']:
                query = query.replace(word, '').strip()
            
            if query:
                self.browser.search_google(query)
                self.speak(f"Searching for {query}")
            else:
                self.speak("What should I search for?")
            return True
        
        # YouTube
        elif 'youtube' in action_lower:
            query = action_lower.replace('youtube', '').strip()
            for word in ['play', 'for', 'please']:
                query = query.replace(word, '').strip()
            
            if query:
                self.browser.search_youtube(query)
                self.speak(f"Playing {query} on YouTube")
            else:
                self.speak("What should I play on YouTube?")
            return True
        
        # Joke
        elif 'joke' in action_lower or 'funny' in action_lower:
            self.speak(self.ai.tell_joke())
            return True
        
        # Motivation
        elif 'motivate' in action_lower or 'quote' in action_lower or 'inspire' in action_lower:
            self.speak(self.ai.get_motivation())
            return True
        
        return False
    
    def process_command(self, command):
        if not command or self.processing:
            return
        
        self.processing = True
        command = command.strip().lower()
        self.log(f"Command: {command}")
        
        try:
            # Conversation mode
            if 'start conversation' in command:
                self.conversation_active = True
                self.speak("Continuous mode started!")
                self.processing = False
                return
            
            if 'stop conversation' in command or 'end conversation' in command:
                self.conversation_active = False
                self.speak("Continuous mode stopped")
                self.processing = False
                return
            
            # If in conversation mode
            if self.conversation_active:
                if 'exit' in command or 'goodbye' in command:
                    self.speak(self.ai.get_farewell())
                    self.conversation_active = False
                    self.processing = False
                    return
                
                if self.execute_action(command):
                    self.processing = False
                    return
                
                self.speak("Thinking...")
                response = self.ai.process_command(command)
                extracted = self.ai.extract_command(response)
                
                if extracted['type'] == 'action':
                    self.speak(extracted['response'])
                    self.execute_action(extracted['action'])
                else:
                    self.speak(extracted['response'])
                self.processing = False
                return
            
            # Normal mode
            if 'exit' in command or 'goodbye' in command:
                self.speak(self.ai.get_farewell())
                self.running = False
                self.processing = False
                return
            
            # Try to execute
            if self.execute_action(command):
                self.processing = False
                return
            
            # If nothing matches, use AI
            self.speak("Thinking...")
            response = self.ai.process_command(command)
            extracted = self.ai.extract_command(response)
            
            if extracted['type'] == 'action':
                self.speak(extracted['response'])
                self.execute_action(extracted['action'])
            else:
                self.speak(extracted['response'])
                
        except Exception as e:
            self.speak("Error")
            self.log(f"Error: {e}")
        finally:
            self.processing = False
    
    def listen_continuously(self):
        """Listening with improved command detection"""
        if not self.recognizer or not self.microphone:
            self.speak("Microphone not available")
            return
        
        try:
            with self.microphone as source:
                print(f"\n🎤 Listening... Say '{self.WAKE_WORD}' + command")
                print(f"💡 Examples: '{self.WAKE_WORD} time', '{self.WAKE_WORD} search Python'")
                print("💡 Speak slowly and clearly\n")
                
                while self.running:
                    try:
                        if self.processing:
                            time.sleep(0.1)
                            continue
                        
                        print("👂", end=" ", flush=True)
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                        
                        try:
                            text = self.recognizer.recognize_google(audio, language='en-US')
                            print(f"\n👤 You: {text}")
                            
                            text_lower = text.lower()
                            
                            # Check for wake word
                            if self.WAKE_WORD in text_lower:
                                # Remove wake word
                                clean = text_lower.replace(self.WAKE_WORD, '').strip()
                                
                                # Clean extra spaces
                                while '  ' in clean:
                                    clean = clean.replace('  ', ' ')
                                
                                if clean:
                                    self.speak("Yes?")
                                    self.process_command(clean)
                                else:
                                    self.speak("Yes boss?")
                                    try:
                                        cmd_audio = self.recognizer.listen(source, timeout=4, phrase_time_limit=8)
                                        cmd_text = self.recognizer.recognize_google(cmd_audio, language='en-US')
                                        print(f"👤 Command: {cmd_text}")
                                        self.process_command(cmd_text.lower())
                                    except:
                                        pass
                            
                            # Direct commands (without wake word)
                            elif self.conversation_active:
                                self.process_command(text_lower)
                            
                            elif any(word in text_lower for word in ['open', 'search', 'time', 'date', 'status']):
                                self.process_command(text_lower)
                        
                        except sr.UnknownValueError:
                            pass
                        except sr.RequestError:
                            print("⚠️ Network error")
                            time.sleep(1)
                        
                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        print(f"⚠️ Error: {e}")
                        continue
                        
        except Exception as e:
            print(f"❌ Microphone error: {e}")
            self.speak("Microphone error")
    
    def run_voice_mode(self):
        try:
            self.greet()
            self.listen_continuously()
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            self.speak("Goodbye boss!")
        except Exception as e:
            print(f"❌ Error: {e}")
            self.speak("Error")

if __name__ == "__main__":
    try:
        jarvis = Jarvis()
        jarvis.run_voice_mode()
    except KeyboardInterrupt:
        print("\n👋 JARVIS shut down")
    except Exception as e:
        print(f"❌ Fatal Error: {e}")