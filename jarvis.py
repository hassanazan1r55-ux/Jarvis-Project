import sys
import os
import json
import time
import threading
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Now import from modules
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
    ║     🚀 JARVIS AI ASSISTANT v5.0              ║
    ║     Natural Conversation Flow                 ║
    ║     Say "Jarvis" + command                   ║
    ╚═══════════════════════════════════════════════╝
        """)
        
        # Check for .env file
        if not os.path.exists('.env'):
            print("⚠️ WARNING: .env file not found!\n")
        
        # Load config
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print("❌ config.json not found! Creating default...")
            self.config = self._create_default_config()
        
        # Set user name
        self.user_name = self.config.get('USER_NAME', 'Boss')
        self.is_listening = False
        self.conversation_active = False
        self.processing = False
        self.waiting_for_command = False  # New: waiting state
        
        # Initialize managers
        self.system = SystemManager()
        self.browser = BrowserManager()
        self.ai = AIManager()
        
        # Voice engine setup
        self.engine = None
        if VOICE_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 170)  # Normal speed
                self.engine.setProperty('volume', 0.9)
                
                voices = self.engine.getProperty('voices')
                if voices and self.config.get('VOICE_GENDER') == 'female':
                    self.engine.setProperty('voice', voices[1].id)
                elif voices:
                    self.engine.setProperty('voice', voices[0].id)
            except Exception as e:
                print(f"⚠️ Voice engine error: {e}")
                self.engine = None
        
        # Microphone setup - Balanced
        self.recognizer = None
        if MIC_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                # BALANCED SETTINGS
                self.recognizer.energy_threshold = 350
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.dynamic_energy_adjustment_damping = 0.1
                self.recognizer.dynamic_energy_ratio = 1.5
                self.recognizer.pause_threshold = 0.5  # Normal pause
                self.recognizer.phrase_threshold = 0.3
                self.recognizer.non_speaking_duration = 0.3
                
                print("✅ Microphone configured for natural conversation!")
            except Exception as e:
                print(f"⚠️ Microphone error: {e}")
                self.recognizer = None
        
        self.running = True
        self.log_file = 'logs/history.log'
        os.makedirs('logs', exist_ok=True)
        
        self.log("JARVIS Started")
        print("✅ JARVIS is ready!")
        print("🎤 Say 'Jarvis' + command (e.g., 'Jarvis what's the time')")
        print("💬 Or say 'Start Conversation' for continuous mode\n")
    
    def _create_default_config(self):
        """Create default config if not exists"""
        default_config = {
            "USER_NAME": "Boss",
            "VOICE_SPEED": 170,
            "VOICE_VOLUME": 0.9,
            "VOICE_GENDER": "male",
            "OPENROUTER_MODEL": "openai/gpt-3.5-turbo",
            "MAX_TOKENS": 200,
            "TEMPERATURE": 0.7,
            "MAX_HISTORY": 10,
            "BROWSER_PATH": "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "APPS": {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe",
                "word": "winword.exe",
                "excel": "excel.exe",
                "spotify": "spotify.exe",
                "vscode": "code.exe",
                "paint": "mspaint.exe",
                "cmd": "cmd.exe",
                "edge": "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
            },
            "WEBSITES": {
                "google": "https://www.google.com",
                "youtube": "https://www.youtube.com",
                "github": "https://www.github.com",
                "gmail": "https://mail.google.com",
                "stackoverflow": "https://stackoverflow.com",
                "chatgpt": "https://chat.openai.com"
            }
        }
        with open('config.json', 'w') as f:
            json.dump(default_config, f, indent=4)
        print("✅ Default config.json created!")
        return default_config
    
    def speak(self, text):
        """Speak naturally"""
        print(f"🤖 JARVIS: {text}")
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"⚠️ Speak error: {e}")
    
    def log(self, message):
        """Log activities"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
        except:
            pass
    
    def greet(self):
        """Greeting on startup"""
        try:
            greeting = self.ai.get_greeting()
            self.speak(greeting)
            self.speak("Say Jarvis and your command, or start a conversation!")
        except Exception as e:
            self.speak(f"Hello! I'm JARVIS. How can I help?")
            print(f"⚠️ Greeting error: {e}")
    
    def execute_action(self, action):
        """Execute system actions"""
        if not action:
            return False
        
        action_lower = action.lower()
        
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
            for app in ['notepad', 'calculator', 'chrome', 'word', 'excel', 'spotify', 
                       'vscode', 'paint', 'cmd', 'edge']:
                if app in action_lower:
                    result = self.system.open_app(app)
                    self.speak(result)
                    self.log(f"Opened: {app}")
                    return True
            self.speak("I don't know that app")
            return True
        
        # Close apps
        elif 'close' in action_lower or 'kill' in action_lower:
            for app in ['notepad', 'chrome', 'word', 'excel', 'spotify', 'edge']:
                if app in action_lower:
                    result = self.system.close_app(app)
                    self.speak(result)
                    self.log(f"Closed: {app}")
                    return True
            self.speak("I don't know that app")
            return True
        
        # Screenshot
        elif 'screenshot' in action_lower or 'capture' in action_lower:
            result = self.system.take_screenshot()
            self.speak(result)
            self.log("Screenshot taken")
            return True
        
        # System status
        elif 'status' in action_lower or 'battery' in action_lower:
            try:
                status = self.system.get_system_status()
                bat = status['battery']
                status_msg = f"Battery at {bat['percent']} percent, {'charging' if bat['plugged'] else 'on battery'}"
                self.speak(status_msg)
                self.log("System status checked")
            except:
                self.speak("Unable to get system status")
            return True
        
        # Shutdown
        elif 'shutdown' in action_lower:
            self.speak("Shutting down in 10 seconds. Goodbye boss!")
            self.log("Shutdown initiated")
            self.running = False
            time.sleep(2)
            try:
                os.system("shutdown /s /t 10")
            except:
                pass
            return True
        
        # Restart
        elif 'restart' in action_lower or 'reboot' in action_lower:
            self.speak("Restarting in 10 seconds")
            self.log("Restart initiated")
            self.running = False
            time.sleep(2)
            try:
                os.system("shutdown /r /t 10")
            except:
                pass
            return True
        
        # Lock
        elif 'lock' in action_lower:
            try:
                self.system.lock_system()
                self.speak("System locked")
                self.log("System locked")
            except:
                self.speak("Unable to lock system")
            return True
        
        # Google Search
        elif 'search' in action_lower:
            query = action_lower.replace('search', '').strip()
            if query:
                try:
                    result = self.browser.search_google(query)
                    self.speak(result)
                    self.log(f"Searched: {query}")
                except:
                    self.speak("Unable to search")
                return True
        
        # YouTube
        elif 'youtube' in action_lower:
            query = action_lower.replace('youtube', '').strip()
            if query:
                try:
                    result = self.browser.search_youtube(query)
                    self.speak(result)
                    self.log(f"YouTube: {query}")
                except:
                    self.speak("Unable to open YouTube")
                return True
        
        # Open Website
        elif 'open website' in action_lower or 'go to' in action_lower:
            for site in ['google', 'youtube', 'github', 'gmail', 'stackoverflow', 'chatgpt']:
                if site in action_lower:
                    try:
                        result = self.browser.open_website(site)
                        self.speak(result)
                        self.log(f"Opened website: {site}")
                    except:
                        self.speak(f"Unable to open {site}")
                    return True
        
        return False
    
    def process_command(self, command):
        """Process command with proper flow"""
        if not command:
            return
        
        if self.processing:
            return
        
        self.processing = True
        command = command.strip().lower()
        self.log(f"Processing: {command}")
        
        try:
            # Check for conversation mode toggle
            if 'start conversation' in command:
                self.conversation_active = True
                self.speak("Starting continuous conversation mode. Just talk to me naturally!")
                self.processing = False
                return
            
            if 'stop conversation' in command or 'end conversation' in command:
                self.conversation_active = False
                self.speak("Exiting continuous conversation mode")
                self.processing = False
                return
            
            # If in conversation mode
            if self.conversation_active:
                # Check for exit
                if 'exit' in command or 'goodbye' in command:
                    self.speak(self.ai.get_farewell())
                    self.conversation_active = False
                    self.processing = False
                    return
                
                # Check for joke/motivation
                if 'joke' in command or 'funny' in command:
                    joke = self.ai.tell_joke()
                    self.speak(joke)
                    self.processing = False
                    return
                
                if 'motivate' in command or 'quote' in command:
                    quote = self.ai.get_motivation()
                    self.speak(quote)
                    self.processing = False
                    return
                
                # Try system action
                if self.execute_action(command):
                    self.processing = False
                    return
                
                # Use AI for conversation
                self.speak("Let me think about that...")
                ai_response = self.ai.process_command(command)
                extracted = self.ai.extract_command(ai_response)
                
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
            
            # Check for joke/motivation
            if 'joke' in command:
                joke = self.ai.tell_joke()
                self.speak(joke)
                self.processing = False
                return
            
            if 'motivate' in command or 'quote' in command:
                quote = self.ai.get_motivation()
                self.speak(quote)
                self.processing = False
                return
            
            # Try system action
            if self.execute_action(command):
                self.processing = False
                return
            
            # Use AI
            self.speak("Let me think about that...")
            ai_response = self.ai.process_command(command)
            extracted = self.ai.extract_command(ai_response)
            
            if extracted['type'] == 'action':
                self.speak(extracted['response'])
                self.execute_action(extracted['action'])
            else:
                self.speak(extracted['response'])
                
        except Exception as e:
            self.speak("Sorry, something went wrong")
            self.log(f"Error: {e}")
        finally:
            self.processing = False
    
    def listen_continuously(self):
        """Natural conversation flow with proper timing"""
        if not MIC_AVAILABLE or not self.recognizer:
            self.speak("Microphone not available")
            print("❌ Microphone not available!")
            return
        
        try:
            with sr.Microphone() as source:
                print("🎤 Calibrating microphone...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("🎤 Ready! Listening for commands...")
                print("="*50)
                
                while self.running:
                    try:
                        if self.processing:
                            time.sleep(0.1)
                            continue
                        
                        # Listen with proper timeout
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                        
                        try:
                            text = self.recognizer.recognize_google(audio, language='en-US')
                            print(f"👤 You: {text}")
                            
                            # Check for wake word
                            if 'jarvis' in text.lower():
                                # Remove "jarvis" from command
                                clean_command = text.lower().replace('jarvis', '').strip()
                                
                                if clean_command:
                                    # Has command with wake word
                                    self.process_command(clean_command)
                                else:
                                    # Only "jarvis" - wait for command
                                    self.speak("Yes boss? How can I help you?")
                                    
                                    # Listen for command
                                    try:
                                        cmd_audio = self.recognizer.listen(source, timeout=4, phrase_time_limit=8)
                                        cmd_text = self.recognizer.recognize_google(cmd_audio, language='en-US')
                                        print(f"👤 Command: {cmd_text}")
                                        self.process_command(cmd_text.lower())
                                    except sr.WaitTimeoutError:
                                        self.speak("I didn't catch that. Say again?")
                                    except sr.UnknownValueError:
                                        self.speak("I didn't understand that")
                            
                            # If in conversation mode, process without wake word
                            elif self.conversation_active:
                                self.process_command(text.lower())
                            
                            # Direct commands for quick actions
                            elif any(word in text.lower() for word in ['open', 'search', 'time', 'date', 'status']):
                                self.process_command(text.lower())
                        
                        except sr.UnknownValueError:
                            # Silently ignore unclear speech
                            pass
                        except sr.RequestError:
                            print("⚠️ Network error")
                            time.sleep(1)
                        
                    except sr.WaitTimeoutError:
                        # No speech detected, continue listening
                        continue
                    except Exception as e:
                        print(f"⚠️ Error: {e}")
                        continue
                        
        except Exception as e:
            print(f"❌ Microphone error: {e}")
            self.speak("Microphone error. Please check your settings.")
    
    def run_voice_mode(self):
        """Main voice mode loop"""
        try:
            self.greet()
            self.listen_continuously()
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            self.speak("Goodbye boss!")
        except Exception as e:
            print(f"❌ Error: {e}")
            self.speak("An error occurred. Restarting...")

if __name__ == "__main__":
    try:
        jarvis = Jarvis()
        jarvis.run_voice_mode()
    except KeyboardInterrupt:
        print("\n👋 JARVIS shut down")
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        try:
            with open('logs/error.log', 'a') as f:
                f.write(f"{datetime.now()}: {str(e)}\n")
        except:
            pass