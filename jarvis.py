import sys
import os
import json
import time
import re
import queue
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
from modules.web_search import WebSearch

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

try:
    import win32com.client
    import pythoncom
    SAPI_AVAILABLE = True
except:
    SAPI_AVAILABLE = False

class Jarvis:
    def __init__(self):
        print("""
    ╔═══════════════════════════════════════════════╗
    ║     🚀 JARVIS AI ASSISTANT v9.9              ║
    ║     TRULY INTERRUPTIBLE SPEECH               ║
    ║     Stop works instantly!                    ║
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
        self.WAKE_WORD = "ai"
        self.conversation_active = False
        self.processing = False
        self.mode = "voice"
        self.speech_enabled = True
        
        # Managers
        self.system = SystemManager()
        self.browser = BrowserManager()
        self.ai = AIManager()
        self.memory = MemoryManager()
        self.personality = PersonalityManager(mode="friendly")
        self.web = WebSearch()
        
        print("🧠 Memory Manager initialized!")
        print(f"🎭 Personality Mode: {self.personality.mode}")
        print("🌐 Web Search Engine initialized!")
        
        # ---------- Shared Engine References ----------
        self.sapi_obj = None
        self.pyttsx_obj = None
        self.engine_lock = threading.Lock()
        
        # ---------- Speech Queue & Worker ----------
        self.speech_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
        
        # ---------- Microphone (ULTRA FAST) ----------
        self.recognizer = None
        self.microphone = None
        if MIC_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.recognizer.energy_threshold = 300
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 0.5
                self.recognizer.phrase_threshold = 0.2
                self.microphone = sr.Microphone()
                print("🎤 Calibrating microphone...")
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"✅ Microphone ready! Energy threshold: {self.recognizer.energy_threshold}")
            except Exception as e:
                print(f"⚠️ Microphone error: {e}")
                self.recognizer = None
        
        self.running = True
        self.log_file = 'logs/history.log'
        os.makedirs('logs', exist_ok=True)
        self.log("JARVIS Started (v9.9)")
        
        print("\n✅ JARVIS is ready!")
        print(f"🎤 Voice Mode: Say '{self.WAKE_WORD}' + command")
        print("⌨️  Text Mode: Type 'ai' + command")
        print("🛑 Say 'stop' or 'mute' instantly")
        print("🌐 Internet: search, weather, news")
        print("="*50)
        
        self.greet()
        self.run_voice_mode()
    
    # ---------- Configuration ----------
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
    
    # ---------- Speech Worker (Non-Blocking) ----------
    def _speech_worker(self):
        if SAPI_AVAILABLE:
            try:
                pythoncom.CoInitialize()
            except:
                pass
        
        use_sapi = SAPI_AVAILABLE
        
        # Init engines
        if use_sapi:
            try:
                self.sapi_obj = win32com.client.Dispatch("SAPI.SpVoice")
                print("🔊 SAPI5 ready in worker.")
            except:
                use_sapi = False
                self.sapi_obj = None
        
        if not use_sapi and VOICE_AVAILABLE:
            try:
                self.pyttsx_obj = pyttsx3.init()
                self.pyttsx_obj.setProperty('rate', self.config.get('VOICE_SPEED', 170))
                self.pyttsx_obj.setProperty('volume', self.config.get('VOICE_VOLUME', 0.9))
                print("🔊 pyttsx3 ready in worker.")
                # For non-blocking pyttsx3, we use event loop
                self.pyttsx_obj.startLoop(False)
            except:
                self.pyttsx_obj = None
        
        while True:
            text = self.speech_queue.get()
            if text is None:
                break
            
            # Check stop
            if self.stop_event.is_set():
                self.stop_event.clear()
                self.speech_queue.task_done()
                continue
            
            if not self.speech_enabled:
                self.speech_queue.task_done()
                continue
            
            clean = self._remove_emojis(text)
            if not clean:
                self.speech_queue.task_done()
                continue
            
            # ---- Speak with SAPI5 (Async) ----
            if use_sapi and self.sapi_obj:
                try:
                    # SVSFAsync = 1, SVSFPurgeBeforeSpeak = 3 (for stop)
                    self.sapi_obj.Speak(clean, 1)  # Async
                    # Wait while speech is playing, but check stop_event every 50ms
                    while True:
                        if self.stop_event.is_set():
                            # Purge immediately
                            self.sapi_obj.Speak("", 3)
                            self.stop_event.clear()
                            break
                        time.sleep(0.05)
                        # Check if speech finished (optional, but we can break after a timeout)
                        # We'll just loop until stop or a small timeout; but we need to not block forever.
                        # We'll use a simple loop with a max duration (long sentences may exceed)
                        # Simpler: wait a bit then break; but we want to be able to interrupt,
                        # so we check stop_event in the loop.
                        # However, we need to know when speech finishes to break properly.
                        # SAPI5 doesn't provide a simple status check, so we'll use a timer.
                        # We'll set a max wait time based on text length (approximate).
                        # But for interruptibility, we'll just check stop_event in a loop for a limited time.
                        # After a reasonable time, we break and continue.
                        # We'll estimate 100ms per word.
                        word_count = len(clean.split())
                        wait_time = min(word_count * 0.1, 30)  # max 30 seconds
                        # We already have a while loop; we'll break after that time.
                        # But we also want to break if stop_event is set.
                        # We'll use a start time.
                        if not hasattr(self, '_sapi_start'):
                            self._sapi_start = time.time()
                        if time.time() - self._sapi_start > wait_time:
                            break
                    # Clean up timer
                    if hasattr(self, '_sapi_start'):
                        del self._sapi_start
                    self.speech_queue.task_done()
                    continue
                except Exception as e:
                    print(f"⚠️ SAPI5 error: {e}")
                    use_sapi = False
                    self.sapi_obj = None
            
            # ---- Speak with pyttsx3 (Non-Blocking with iterate) ----
            if self.pyttsx_obj:
                try:
                    self.pyttsx_obj.say(clean)
                    # Iterate until finished or stop
                    while True:
                        if self.stop_event.is_set():
                            self.pyttsx_obj.stop()
                            self.stop_event.clear()
                            break
                        # iterate() returns True if still speaking
                        if not self.pyttsx_obj.iterate():
                            break
                        time.sleep(0.05)
                    self.speech_queue.task_done()
                    continue
                except Exception as e:
                    print(f"⚠️ pyttsx3 error: {e}")
                    self.pyttsx_obj = None
            
            # If both fail
            print(f"⚠️ Could not speak: {clean[:30]}...")
            self.speech_queue.task_done()
    
    def _remove_emojis(self, text):
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F700-\U0001F77F"
            u"\U0001F780-\U0001F7FF"
            u"\U0001F800-\U0001F8FF"
            u"\U0001F900-\U0001F9FF"
            u"\U0001FA00-\U0001FA6F"
            u"\U0001FA70-\U0001FAFF"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text).strip()
    
    # ---------- Speak (Queue) ----------
    def speak(self, text):
        print(f"🤖 JARVIS: {text}")
        if text and self.speech_enabled:
            self.speech_queue.put(text)
    
    # ---------- Immediate Stop/Mute ----------
    def stop_speech(self):
        self.stop_event.set()
        # Clear queue
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except:
                break
        # Additional purge (redundant but safe)
        if self.sapi_obj:
            try:
                self.sapi_obj.Speak("", 3)
            except:
                pass
        if self.pyttsx_obj:
            try:
                self.pyttsx_obj.stop()
            except:
                pass
        print("🛑 Speech stopped.")
    
    def mute(self):
        self.speech_enabled = False
        self.stop_speech()
        print("🔇 Muted.")
    
    def unmute(self):
        self.speech_enabled = True
        print("🔊 Unmuted.")
        self.speak("Speech resumed.")
    
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
            greeting += " I'm JARVIS. Tell me your name and I'll remember it!"
        self.speak(greeting)
    
    # ---------- Internet Commands ----------
    def execute_internet_action(self, action):
        action_lower = action.lower()
        if 'search' in action_lower:
            query = action_lower.replace('search', '').strip()
            if not query:
                self.speak("What should I search for?")
                return True
            self.speak(f"Searching for {query}...")
            result = self.web.search(query)
            self.speak(result)
            return True
        elif 'weather' in action_lower:
            city = "Karachi"
            words = action_lower.split()
            for w in words:
                if w.lower() not in ['weather', 'what', 'is', 'the', 'in', 'for']:
                    city = w.capitalize()
            self.speak(f"Fetching weather for {city}...")
            result = self.web.get_weather(city)
            self.speak(result)
            return True
        elif 'news' in action_lower:
            topic = action_lower.replace('news', '').strip()
            if not topic:
                topic = "latest"
            self.speak(f"Fetching news about {topic}...")
            result = self.web.get_news(topic)
            self.speak(result)
            return True
        return False
    
    # ---------- Execute Action ----------
    def execute_action(self, action):
        if not action:
            return False
        action_lower = action.lower()
        self.log(f"Executing: {action_lower}")
        
        # ---- Immediate commands ----
        if action_lower in ['stop', 'shut up', 'silence', 'enough']:
            self.stop_speech()
            return True
        if action_lower == 'mute':
            self.mute()
            return True
        if action_lower == 'unmute':
            self.unmute()
            return True
        
        # ---- System ----
        if 'time' in action_lower and 'date' not in action_lower:
            self.speak(f"The time is {self.system.get_time()}")
            return True
        if 'date' in action_lower:
            self.speak(f"Today is {self.system.get_date()}")
            return True
        if 'open' in action_lower:
            for app in ['notepad', 'calculator', 'chrome', 'word', 'excel', 'spotify', 'vscode', 'paint', 'cmd']:
                if app in action_lower:
                    self.speak(self.system.open_app(app))
                    return True
            self.speak("I don't know that app")
            return True
        if 'close' in action_lower:
            for app in ['notepad', 'chrome', 'word', 'excel', 'spotify']:
                if app in action_lower:
                    self.speak(self.system.close_app(app))
                    return True
            self.speak("I don't know that app")
            return True
        if 'screenshot' in action_lower:
            self.speak(self.system.take_screenshot())
            return True
        if 'status' in action_lower or 'battery' in action_lower:
            try:
                status = self.system.get_system_status()
                bat = status['battery']
                self.speak(f"Battery {bat['percent']}%, {'charging' if bat['plugged'] else 'on battery'}")
            except:
                self.speak("Can't get status")
            return True
        if 'youtube' in action_lower:
            query = action_lower.replace('youtube', '').strip()
            if query:
                self.browser.search_youtube(query)
                self.speak(f"Playing {query} on YouTube")
            return True
        if 'joke' in action_lower:
            self.speak(self.ai.tell_joke())
            return True
        if 'motivate' in action_lower or 'quote' in action_lower:
            self.speak(self.ai.get_motivation())
            return True
        
        # ---- Memory ----
        if 'my name is' in action_lower or 'call me' in action_lower:
            if 'my name is' in action_lower:
                name = action_lower.split('my name is')[-1].strip()
            else:
                name = action_lower.split('call me')[-1].strip()
            if name:
                self.memory.remember_user("name", name.title())
                self.speak(f"I'll remember your name is {name.title()}!")
            return True
        if 'my name' in action_lower and ('what' in action_lower or 'kya' in action_lower):
            name = self.memory.get_user_info("name")
            if name:
                self.speak(f"Your name is {name}, boss!")
            else:
                self.speak("I don't remember your name yet.")
            return True
        
        # ---- Personality ----
        if 'change to' in action_lower:
            for mode in ["professional", "friendly", "funny", "strict", "emotional"]:
                if mode in action_lower:
                    self.speak(self.personality.change_mode(mode))
                    return True
        if 'personality' in action_lower or 'mode' in action_lower:
            self.speak(f"I'm currently in {self.personality.mode} mode!")
            return True
        
        # ---- Tasks ----
        if 'remind me' in action_lower or 'add task' in action_lower:
            task = action_lower.replace('remind me to', '').replace('add task', '').strip()
            if task:
                self.memory.add_task(task, None)
                self.speak(f"Task added: {task}")
            else:
                self.speak("What task?")
            return True
        if 'my tasks' in action_lower:
            tasks = self.memory.get_pending_tasks()
            if tasks:
                task_list = "\n".join([f"  - {t['task']} (ID: {t['id']})" for t in tasks])
                self.speak(f"Your tasks:\n{task_list}")
            else:
                self.speak("No tasks.")
            return True
        if 'complete task' in action_lower:
            import re
            nums = re.findall(r'\d+', action_lower)
            if nums:
                self.speak(self.memory.complete_task(int(nums[0])))
            else:
                self.speak("Task ID?")
            return True
        
        # ---- Habits ----
        if 'add habit' in action_lower:
            habit = action_lower.replace('add habit', '').strip()
            if habit:
                self.memory.add_habit(habit, None)
                self.speak(f"Habit added: {habit}")
            else:
                self.speak("What habit?")
            return True
        if 'habit done' in action_lower:
            habit = action_lower.replace('habit done', '').strip()
            if habit:
                self.speak(self.memory.complete_habit(habit))
            else:
                self.speak("Which habit?")
            return True
        
        # ---- Context / Routine ----
        if 'previous conversation' in action_lower:
            context = self.memory.get_recent_context()
            if context:
                self.speak(f"Recent chat:\n{context}")
            else:
                self.speak("No previous.")
            return True
        if 'routine' in action_lower or 'what should i do' in action_lower:
            routine = self.memory.get_daily_routine()
            suggestions = routine.get('suggestions', ['No suggestions'])
            self.speak(f"{routine['time'].title()} routine: {suggestions[0]}")
            return True
        
        # ---- Internet ----
        if self.execute_internet_action(action_lower):
            return True
        
        # ---- Mode ----
        if 'text mode' in action_lower or 'switch to text' in action_lower:
            self.mode = "text"
            self.speak("Text mode.")
            return True
        if 'voice mode' in action_lower or 'switch to voice' in action_lower:
            self.mode = "voice"
            self.speak("Voice mode.")
            return True
        if 'current mode' in action_lower:
            self.speak(f"Mode: {self.mode.upper()}")
            return True
        
        # ---- Help ----
        if 'help' in action_lower or 'commands' in action_lower:
            help_text = """
📋 JARVIS v9.9 Commands:
=========================
🔊 Mute/Unmute: mute, unmute, stop
🌐 Internet: search, weather, news
🕒 System: time, date, status, screenshot
📂 Apps: open/close notepad, chrome, etc.
🧠 Memory: my name is, what's my name
🎭 Personality: change to [mode]
📋 Tasks: remind me, my tasks, complete task
📊 Habits: add habit, habit done
📅 Routine: routine, previous conversation
"""
            self.speak("Commands in console.")
            print(help_text)
            return True
        
        return False
    
    # ---------- Process Command ----------
    def process_command(self, command, source="voice"):
        if not command or self.processing:
            return
        self.processing = True
        command = command.strip().lower()
        self.log(f"Command ({source}): {command}")
        
        try:
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
            if self.conversation_active:
                if 'exit' in command or 'goodbye' in command:
                    self.speak(self.personality.get_farewell())
                    self.conversation_active = False
                    self.processing = False
                    return
                if self.execute_action(command):
                    self.processing = False
                    return
                self.speak(self.personality.get_think())
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
            # Normal
            if 'exit' in command or 'goodbye' in command:
                self.speak(self.personality.get_farewell())
                self.running = False
                self.processing = False
                return
            if self.execute_action(command):
                self.processing = False
                return
            # AI fallback
            self.speak(self.personality.get_think())
            response = self.ai.process_command(command)
            extracted = self.ai.extract_command(response)
            self.memory.add_to_history(command, extracted.get('response', ''))
            if extracted['type'] == 'action':
                self.speak(extracted['response'])
                self.execute_action(extracted['action'])
            else:
                self.speak(extracted['response'])
        except Exception as e:
            self.speak(f"Error: {e}")
            self.log(f"Error: {e}")
        finally:
            self.processing = False
    
    # ---------- ULTRA-FAST Voice Listening ----------
    def listen_voice(self):
        if not self.recognizer or not self.microphone:
            return
        try:
            with self.microphone as source:
                while self.running:
                    try:
                        if self.mode == "text" or self.processing:
                            time.sleep(0.01)
                            continue
                        print("👂", end=" ", flush=True)
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=4)
                        try:
                            text = self.recognizer.recognize_google(audio, language='en-US')
                            print(f"\n🎤 You: {text}")
                            if self.WAKE_WORD in text.lower():
                                clean = text.lower().replace(self.WAKE_WORD, '').strip()
                                if clean:
                                    self.process_command(clean, "voice")
                                else:
                                    self.speak("Yes boss?")
                                    try:
                                        cmd_audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=4)
                                        cmd_text = self.recognizer.recognize_google(cmd_audio, language='en-US')
                                        print(f"🎤 Command: {cmd_text}")
                                        self.process_command(cmd_text.lower(), "voice")
                                    except:
                                        pass
                            elif self.conversation_active:
                                self.process_command(text.lower(), "voice")
                            elif any(word in text.lower() for word in ['open', 'search', 'time', 'date', 'weather', 'stop', 'mute', 'unmute']):
                                self.process_command(text.lower(), "voice")
                        except sr.UnknownValueError:
                            pass
                        except sr.RequestError:
                            print("⚠️ Network error")
                            time.sleep(0.5)
                    except sr.WaitTimeoutError:
                        continue
                    except Exception as e:
                        print(f"⚠️ {e}")
                        continue
        except Exception as e:
            print(f"❌ Microphone error: {e}")
    
    # ---------- Text Input (Main) ----------
    def listen_text(self):
        print("\n⌨️  Type commands (exit to quit).")
        while self.running:
            try:
                if self.mode == "voice":
                    time.sleep(0.2)
                    continue
                cmd = input("🧑 You: ").strip()
                if not cmd:
                    continue
                if cmd.lower() in ['exit', 'quit']:
                    self.speak(self.personality.get_farewell())
                    self.running = False
                    break
                if cmd.lower().startswith('ai'):
                    cmd = cmd[2:].strip()
                self.process_command(cmd, "text")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"⚠️ {e}")
    
    # ---------- Main ----------
    def run_voice_mode(self):
        voice_thread = threading.Thread(target=self.listen_voice, daemon=True)
        voice_thread.start()
        self.listen_text()
        self.running = False
        self.speech_queue.put(None)
        self.speech_thread.join(timeout=1)
        print("👋 JARVIS shut down.")

if __name__ == "__main__":
    jarvis = Jarvis()