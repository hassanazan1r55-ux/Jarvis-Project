import sys
import os
import json
import time
import re
import threading
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.system import SystemManager
from modules.browser import BrowserManager
from modules.ai import AIManager
from modules.memory_manager import MemoryManager
from modules.personality import PersonalityManager

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

# ============================================
# 🔊 TRY SAPI5 (Windows) - MOST RELIABLE
# ============================================
try:
    import win32com.client
    SAPI_AVAILABLE = True
except:
    SAPI_AVAILABLE = False

class Jarvis:
    def __init__(self):
        print("""
    ╔═══════════════════════════════════════════════╗
    ║     🚀 JARVIS AI ASSISTANT v8.8              ║
    ║     VOICE 100% WORKING - NO EMOJI TTS        ║
    ║     Now Speaks ONLY text!                    ║
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
        # 🔥 WAKE WORD
        # ============================================
        self.WAKE_WORD = "ai"
        
        self.conversation_active = False
        self.processing = False
        self.mode = "voice"
        
        # Initialize managers
        self.system = SystemManager()
        self.browser = BrowserManager()
        self.ai = AIManager()
        
        # Memory & Personality
        self.memory = MemoryManager()
        print("🧠 Memory Manager initialized!")
        
        self.personality = PersonalityManager(mode="friendly")
        print(f"🎭 Personality Mode: {self.personality.mode}")
        
        # ============================================
        # 🔊 VOICE ENGINE - SAPI5 (Windows)
        # ============================================
        self.sapi_speaker = None
        self.use_sapi = False
        self.engine = None
        self.voice_available = False
        
        # First try SAPI5 (most reliable on Windows)
        if SAPI_AVAILABLE:
            try:
                print("🔧 Initializing SAPI5 voice engine...")
                self.sapi_speaker = win32com.client.Dispatch("SAPI.SpVoice")
                self.use_sapi = True
                self.voice_available = True
                print("🔊 SAPI5 voice engine initialized!")
                self.speak("Voice engine is ready!")
            except Exception as e:
                print(f"⚠️ SAPI5 error: {e}")
                self.use_sapi = False
        
        # Fallback to pyttsx3 if SAPI5 fails
        if not self.use_sapi and VOICE_AVAILABLE:
            try:
                print("🔧 Initializing pyttsx3 voice engine...")
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', self.config.get('VOICE_SPEED', 170))
                self.engine.setProperty('volume', self.config.get('VOICE_VOLUME', 0.9))
                
                voices = self.engine.getProperty('voices')
                if voices and self.config.get('VOICE_GENDER') == 'female':
                    self.engine.setProperty('voice', voices[1].id)
                elif voices:
                    self.engine.setProperty('voice', voices[0].id)
                
                self.voice_available = True
                print("🔊 pyttsx3 voice engine initialized!")
                self.speak("Voice engine is ready!")
            except Exception as e:
                print(f"⚠️ pyttsx3 error: {e}")
                self.engine = None
                self.voice_available = False
        
        if not self.voice_available:
            print("❌ No voice engine available! Continuing in text-only mode.")
        
        # Microphone setup
        self.recognizer = None
        self.microphone = None
        self.voice_thread = None
        
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
                
            except Exception as e:
                print(f"⚠️ Microphone error: {e}")
                self.recognizer = None
        
        self.running = True
        self.log_file = 'logs/history.log'
        os.makedirs('logs', exist_ok=True)
        
        self.log("JARVIS Started")
        print("\n✅ JARVIS is ready!")
        print(f"🎤 Voice Mode: Say '{self.WAKE_WORD}' + command")
        print("⌨️  Text Mode: Type 'ai' + command")
        print("🔊 JARVIS will SPEAK and TYPE both!")
        print("💡 Type 'help' for all commands")
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
    
    # ============================================
    # 🔧 EMOJI REMOVAL HELPER
    # ============================================
    
    def _remove_emojis(self, text):
        """Remove emojis and special Unicode symbols from text for TTS"""
        # Emoji patterns (most common)
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F700-\U0001F77F"  # alchemical symbols
            u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            u"\U0001FA00-\U0001FA6F"  # Chess Symbols
            u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            u"\U00002702-\U000027B0"  # Dingbats
            u"\U000024C2-\U0001F251" 
            "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text).strip()
    
    # ============================================
    # 🔊 SPEAK FUNCTION - SAPI5 + Fallback
    # ============================================
    
    def speak(self, text):
        """Speak with voice and print (emojis removed from speech only)"""
        # Print original text with emojis
        print(f"🤖 JARVIS: {text}")
        
        if not text or not self.voice_available:
            return
        
        # Remove emojis for speech
        clean_text = self._remove_emojis(text)
        if not clean_text:
            return
        
        # Use SAPI5 (Windows)
        if self.use_sapi and self.sapi_speaker:
            try:
                self.sapi_speaker.Speak(clean_text)
                return
            except Exception as e:
                print(f"⚠️ SAPI5 speak error: {e}")
                # Fallback to pyttsx3
                self.use_sapi = False
        
        # Use pyttsx3
        if self.engine is not None:
            try:
                self.engine.say(clean_text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"⚠️ pyttsx3 speak error: {e}")
                # Try to reinitialize
                try:
                    self.engine = pyttsx3.init()
                    self.engine.setProperty('rate', 170)
                    self.engine.setProperty('volume', 0.9)
                    self.engine.say(clean_text)
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
        greeting = self.personality.get_greeting()
        name = self.memory.get_user_info("name")
        if name:
            greeting = f"{greeting} Great to see you again, {name}!"
        else:
            greeting += " I'm JARVIS. You can tell me your name and I'll remember it!"
        
        self.speak(greeting)
    
    def execute_action(self, action):
        if not action:
            return False
        
        action_lower = action.lower()
        self.log(f"Executing: {action_lower}")
        
        # ============================================
        # 🧠 MEMORY COMMANDS
        # ============================================
        
        # Remember name
        if 'my name is' in action_lower or 'call me' in action_lower:
            if 'my name is' in action_lower:
                name = action_lower.split('my name is')[-1].strip()
            elif 'call me' in action_lower:
                name = action_lower.split('call me')[-1].strip()
            
            if name:
                self.memory.remember_user("name", name.title())
                response = self.personality.get_acknowledge()
                self.speak(f"{response} I'll remember your name is {name.title()}!")
                return True
        
        # What's my name
        elif 'my name' in action_lower and ('what' in action_lower or 'kya' in action_lower):
            name = self.memory.get_user_info("name")
            if name:
                self.speak(f"Your name is {name}, boss!")
            else:
                self.speak("I don't remember your name yet. Tell me using: 'My name is ...'")
            return True
        
        # ============================================
        # 🎭 PERSONALITY COMMANDS
        # ============================================
        
        # Change personality
        elif 'change to' in action_lower:
            for mode in ["professional", "friendly", "funny", "strict", "emotional"]:
                if mode in action_lower:
                    result = self.personality.change_mode(mode)
                    self.speak(result)
                    return True
        
        # Current personality
        elif 'personality' in action_lower or 'mode' in action_lower:
            self.speak(f"I'm currently in {self.personality.mode} mode!")
            return True
        
        # ============================================
        # 📋 TASK COMMANDS
        # ============================================
        
        # Add task
        elif 'remind me' in action_lower or 'add task' in action_lower or 'remember to' in action_lower:
            if 'remind me to' in action_lower:
                task = action_lower.split('remind me to')[-1].strip()
            elif 'remember to' in action_lower:
                task = action_lower.split('remember to')[-1].strip()
            else:
                task = action_lower.replace('add task', '').strip()
            
            import re
            time_pattern = r'\b(?:at|@)\s*(\d{1,2}:\d{2}\s*(?:am|pm)?|\d{1,2}\s*(?:am|pm)?)'
            time_match = re.search(time_pattern, action_lower)
            if time_match:
                time_match = time_match.group(1)
            
            result = self.memory.add_task(task, time_match)
            self.speak(result)
            return True
        
        # Show tasks
        elif 'my tasks' in action_lower or 'show tasks' in action_lower or 'pending tasks' in action_lower:
            tasks = self.memory.get_pending_tasks()
            if tasks:
                task_list = "\n".join([f"  - {t['task']} (ID: {t['id']})" for t in tasks])
                self.speak(f"Your pending tasks:\n{task_list}")
            else:
                self.speak("You have no pending tasks!")
            return True
        
        # Complete task
        elif 'complete task' in action_lower or 'task done' in action_lower:
            import re
            numbers = re.findall(r'\d+', action_lower)
            if numbers:
                task_id = int(numbers[0])
                result = self.memory.complete_task(task_id)
                self.speak(result)
            else:
                self.speak("Please provide task ID. Say: Complete task [ID]")
            return True
        
        # ============================================
        # 📊 HABIT COMMANDS
        # ============================================
        
        # Add habit
        elif 'add habit' in action_lower or 'habit of' in action_lower:
            if 'habit of' in action_lower:
                habit = action_lower.split('habit of')[-1].strip()
            else:
                habit = action_lower.replace('add habit', '').strip()
            
            import re
            time_pattern = r'\b(?:at|@)\s*(\d{1,2}:\d{2}\s*(?:am|pm)?|\d{1,2}\s*(?:am|pm)?)'
            time_match = re.search(time_pattern, action_lower)
            if time_match:
                time_match = time_match.group(1)
            
            result = self.memory.add_habit(habit, time_match)
            self.speak(result)
            return True
        
        # Complete habit
        elif 'habit done' in action_lower:
            habit = action_lower.replace('habit done', '').strip()
            if habit:
                result = self.memory.complete_habit(habit)
                self.speak(result)
            else:
                self.speak("Which habit did you complete?")
            return True
        
        # ============================================
        # 🔍 CONTEXT AWARENESS
        # ============================================
        
        # Previous conversation
        elif 'previous conversation' in action_lower or 'what did we talk about' in action_lower:
            context = self.memory.get_recent_context()
            if context:
                self.speak(f"Here's our recent conversation:\n{context}")
            else:
                self.speak("We haven't had any previous conversations yet.")
            return True
        
        # ============================================
        # 📅 ROUTINE
        # ============================================
        
        # Daily routine
        elif 'routine' in action_lower or 'what should i do' in action_lower:
            routine = self.memory.get_daily_routine()
            suggestions = routine.get('suggestions', ['No suggestions right now'])
            self.speak(f"{routine['time'].title()} routine: {suggestions[0]}")
            return True
        
        # ============================================
        # 🔄 MODE SWITCH
        # ============================================
        
        # Switch to text mode
        elif 'text mode' in action_lower or 'switch to text' in action_lower:
            self.mode = "text"
            self.speak("Switched to Text Mode! Type your commands.")
            return True
        
        # Switch to voice mode
        elif 'voice mode' in action_lower or 'switch to voice' in action_lower:
            self.mode = "voice"
            self.speak("Switched to Voice Mode! Say your commands.")
            return True
        
        # Current mode
        elif 'current mode' in action_lower or 'what mode' in action_lower:
            self.speak(f"Current mode: {self.mode.upper()}")
            return True
        
        # ============================================
        # 🆘 HELP
        # ============================================
        
        elif 'help' in action_lower or 'commands' in action_lower:
            help_text = """
📋 AVAILABLE COMMANDS:
=======================
🧠 Memory:
  - my name is [name]  - Remember your name
  - what's my name     - Show your name
  
🎭 Personality:
  - change to [mode]   - Professional/Friendly/Funny/Strict/Emotional
  - personality        - Show current mode

📋 Tasks:
  - remind me to [task] - Add task
  - my tasks           - Show pending tasks
  - complete task [id] - Complete task

📊 Habits:
  - add habit of [habit] - Add habit
  - habit done [habit]   - Complete habit

🔍 Context:
  - previous conversation - Show recent chat

📅 Routine:
  - routine / what should i do - Daily suggestions

🔄 Mode:
  - text mode / switch to text - Text input mode
  - voice mode / switch to voice - Voice input mode

💻 System:
  - time, date, status
  - open [app], close [app]
  - search [query], youtube [query]
  - joke, motivate, screenshot

💡 Type 'help' to see this menu again
"""
            self.speak("Here are all available commands!")
            print(help_text)
            return True
        
        # ============================================
        # EXISTING COMMANDS
        # ============================================
        
        # Time
        elif 'time' in action_lower and 'date' not in action_lower:
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
            for app in ['notepad', 'calculator', 'chrome', 'word', 'excel', 'spotify', 'vscode', 'paint', 'cmd']:
                if app in action_lower:
                    result = self.system.open_app(app)
                    self.speak(result)
                    return True
            self.speak("I don't know that app")
            return True
        
        # Close apps
        elif 'close' in action_lower:
            for app in ['notepad', 'chrome', 'word', 'excel', 'spotify']:
                if app in action_lower:
                    result = self.system.close_app(app)
                    self.speak(result)
                    return True
            self.speak("I don't know that app")
            return True
        
        # Screenshot
        elif 'screenshot' in action_lower:
            result = self.system.take_screenshot()
            self.speak(result)
            return True
        
        # Status
        elif 'status' in action_lower or 'battery' in action_lower:
            try:
                status = self.system.get_system_status()
                bat = status['battery']
                self.speak(f"Battery {bat['percent']}%, {'charging' if bat['plugged'] else 'on battery'}")
            except:
                self.speak("Can't get status")
            return True
        
        # Search
        elif 'search' in action_lower:
            query = action_lower.replace('search', '').strip()
            if query:
                self.browser.search_google(query)
                self.speak(f"Searching for {query}")
            return True
        
        # YouTube
        elif 'youtube' in action_lower:
            query = action_lower.replace('youtube', '').strip()
            if query:
                self.browser.search_youtube(query)
                self.speak(f"Playing {query} on YouTube")
            return True
        
        # Joke
        elif 'joke' in action_lower:
            joke = self.ai.tell_joke()
            self.speak(joke)
            return True
        
        # Motivation
        elif 'motivate' in action_lower or 'quote' in action_lower:
            self.speak(self.ai.get_motivation())
            return True
        
        # ============================================
        # FALLBACK: AI RESPONSE
        # ============================================
        
        return False
    
    def process_command(self, command, source="voice"):
        if not command or self.processing:
            return
        
        self.processing = True
        command = command.strip().lower()
        self.log(f"Command ({source}): {command}")
        
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
                    farewell = self.personality.get_farewell()
                    self.speak(farewell)
                    self.conversation_active = False
                    self.processing = False
                    return
                
                if self.execute_action(command):
                    self.processing = False
                    return
                
                think = self.personality.get_think()
                self.speak(think)
                response = self.ai.process_command(command)
                extracted = self.ai.extract_command(response)
                
                self.memory.add_to_history(command, extracted.get('response', ''))
                
                if extracted['type'] == 'action':
                    self.speak(extracted['response'])
                    self.execute_action(extracted['action'])
                else:
                    self.speak(extracted['response'])
                self.processing = False
                return
            
            # Normal mode
            if 'exit' in command or 'goodbye' in command:
                farewell = self.personality.get_farewell()
                self.speak(farewell)
                self.running = False
                self.processing = False
                return
            
            # Execute action
            if self.execute_action(command):
                self.processing = False
                return
            
            # AI fallback
            think = self.personality.get_think()
            self.speak(think)
            response = self.ai.process_command(command)
            extracted = self.ai.extract_command(response)
            
            self.memory.add_to_history(command, extracted.get('response', ''))
            
            if extracted['type'] == 'action':
                self.speak(extracted['response'])
                self.execute_action(extracted['action'])
            else:
                self.speak(extracted['response'])
                
        except Exception as e:
            error_msg = self.personality.get_error()
            self.speak(f"{error_msg} {str(e)}")
            self.log(f"Error: {e}")
        finally:
            self.processing = False
    
    def listen_voice(self):
        """Voice listening thread"""
        if not self.recognizer or not self.microphone:
            return
        
        try:
            with self.microphone as source:
                while self.running:
                    try:
                        if self.mode == "text" or self.processing:
                            time.sleep(0.1)
                            continue
                        
                        print("👂", end=" ", flush=True)
                        audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=8)
                        
                        try:
                            text = self.recognizer.recognize_google(audio, language='en-US')
                            print(f"\n🎤 You: {text}")
                            
                            if self.WAKE_WORD in text.lower():
                                clean = text.lower().replace(self.WAKE_WORD, '').strip()
                                if clean:
                                    acknowledge = self.personality.get_acknowledge()
                                    self.speak(acknowledge)
                                    self.process_command(clean, "voice")
                                else:
                                    yes = self.personality.get_yes()
                                    self.speak(f"{yes} How can I help?")
                                    try:
                                        cmd_audio = self.recognizer.listen(source, timeout=4, phrase_time_limit=8)
                                        cmd_text = self.recognizer.recognize_google(cmd_audio, language='en-US')
                                        print(f"🎤 Command: {cmd_text}")
                                        self.process_command(cmd_text.lower(), "voice")
                                    except:
                                        pass
                            
                            elif self.conversation_active:
                                self.process_command(text.lower(), "voice")
                            
                            elif any(word in text.lower() for word in ['open', 'search', 'time', 'date']):
                                self.process_command(text.lower(), "voice")
                        
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
    
    def listen_text(self):
        """Text input listener"""
        print("\n⌨️  Text Mode Active! Type your commands.")
        print("💡 Type 'help' for commands, 'voice mode' to switch back\n")
        
        while self.running:
            try:
                if self.mode == "voice":
                    time.sleep(0.5)
                    continue
                
                command = input("🧑 You: ").strip()
                
                if not command:
                    continue
                
                if command.lower() == 'exit' or command.lower() == 'quit':
                    farewell = self.personality.get_farewell()
                    self.speak(farewell)
                    self.running = False
                    break
                
                if command.lower().startswith('ai'):
                    command = command[2:].strip()
                
                self.process_command(command, "text")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"⚠️ Error: {e}")
    
    def run_voice_mode(self):
        """Main loop with both voice and text"""
        try:
            self.greet()
            
            # Start voice thread
            voice_thread = threading.Thread(target=self.listen_voice, daemon=True)
            voice_thread.start()
            
            # Start text input in main thread
            self.listen_text()
            
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            farewell = self.personality.get_farewell()
            self.speak(farewell)
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