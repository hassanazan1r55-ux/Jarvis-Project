import sys
import os
import json
import time
import threading
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
        print("""
    ╔════════════════════════════════════════╗
    ║     🚀 JARVIS AI ASSISTANT v3.0       ║
    ║     Voice Mode Active                  ║
    ║     Say "Jarvis" to activate          ║
    ╚════════════════════════════════════════╝
        """)
        
        # Check for .env file
        if not os.path.exists('.env'):
            print("⚠️ WARNING: .env file not found!")
            print("   Create .env file with: OPENROUTER_API_KEY=your_key_here")
            print("   Get key from: https://openrouter.ai/keys\n")
        
        # Load config
        with open('config.json', 'r') as f:
            self.config = json.load(f)
        
        self.user_name = self.config.get('USER_NAME', 'Boss')
        self.is_listening = False
        
        # Initialize managers
        self.system = SystemManager()
        self.browser = BrowserManager()
        self.ai = AIManager()
        
        # Voice engine setup
        self.engine = None
        if VOICE_AVAILABLE:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.config.get('VOICE_SPEED', 175))
            self.engine.setProperty('volume', self.config.get('VOICE_VOLUME', 0.9))
            
            # Set voice
            voices = self.engine.getProperty('voices')
            if voices and self.config.get('VOICE_GENDER') == 'female':
                self.engine.setProperty('voice', voices[1].id)
            elif voices:
                self.engine.setProperty('voice', voices[0].id)
        
        # Microphone setup
        self.recognizer = None
        if MIC_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
        
        self.running = True
        self.log_file = 'logs/history.log'
        os.makedirs('logs', exist_ok=True)
        
        self.log("JARVIS Started")
        print("✅ JARVIS is ready!")
        print("🎤 Say 'Jarvis' to wake me up...")
    
    def speak(self, text):
        """Speak with voice"""
        print(f"🤖 JARVIS: {text}")
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except:
                pass
    
    def log(self, message):
        """Log activities"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def greet(self):
        """Greeting on startup"""
        greeting = self.ai.get_greeting()
        self.speak(greeting)
        self.speak("Say Jarvis whenever you need me")
    
    def execute_action(self, action):
        """Execute system actions"""
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
            self.speak("I didn't recognize which app to open")
            return True
        
        # Close apps
        elif 'close' in action_lower or 'kill' in action_lower:
            for app in ['notepad', 'chrome', 'word', 'excel', 'spotify', 'edge']:
                if app in action_lower:
                    result = self.system.close_app(app)
                    self.speak(result)
                    self.log(f"Closed: {app}")
                    return True
            self.speak("I didn't recognize which app to close")
            return True
        
        # Screenshot
        elif 'screenshot' in action_lower or 'capture' in action_lower:
            result = self.system.take_screenshot()
            self.speak(result)
            self.log("Screenshot taken")
            return True
        
        # System status
        elif 'status' in action_lower or 'battery' in action_lower:
            status = self.system.get_system_status()
            bat = status['battery']
            status_msg = f"Battery at {bat['percent']} percent, {'charging' if bat['plugged'] else 'on battery'}"
            status_msg += f". CPU at {status['cpu']} percent, RAM at {status['ram']} percent"
            self.speak(status_msg)
            self.log("System status checked")
            return True
        
        # Shutdown
        elif 'shutdown' in action_lower:
            self.speak("Shutting down system in 10 seconds. Goodbye boss!")
            self.log("Shutdown initiated")
            time.sleep(2)
            os.system("shutdown /s /t 10")
            self.running = False
            return True
        
        # Restart
        elif 'restart' in action_lower or 'reboot' in action_lower:
            self.speak("Restarting system in 10 seconds")
            self.log("Restart initiated")
            time.sleep(2)
            os.system("shutdown /r /t 10")
            self.running = False
            return True
        
        # Lock
        elif 'lock' in action_lower:
            self.system.lock_system()
            self.speak("System locked")
            self.log("System locked")
            return True
        
        # Google Search
        elif 'search' in action_lower:
            query = action_lower.replace('search', '').strip()
            if query:
                result = self.browser.search_google(query)
                self.speak(result)
                self.log(f"Searched: {query}")
                return True
        
        # YouTube
        elif 'youtube' in action_lower:
            query = action_lower.replace('youtube', '').strip()
            if query:
                result = self.browser.search_youtube(query)
                self.speak(result)
                self.log(f"YouTube: {query}")
                return True
        
        # Open Website
        elif 'open' in action_lower:
            for site in ['google', 'youtube', 'github', 'gmail', 'stackoverflow', 'chatgpt']:
                if site in action_lower:
                    result = self.browser.open_website(site)
                    self.speak(result)
                    self.log(f"Opened website: {site}")
                    return True
        
        return False
    
    def listen_continuously(self):
        """Listen for wake word and commands"""
        if not MIC_AVAILABLE:
            self.speak("Microphone not available")
            return
        
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("🎤 Listening for 'Jarvis'...")
            
            while self.running:
                try:
                    # Listen for wake word
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
                    print("🔄 Processing...")
                    
                    try:
                        text = self.recognizer.recognize_google(audio, language='en-US')
                        print(f"📝 Heard: {text}")
                        
                        # Check for wake word
                        if 'jarvis' in text.lower():
                            self.speak("Yes boss? How can I help you?")
                            self.is_listening = True
                            
                            # Listen for actual command
                            try:
                                command_audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                                command_text = self.recognizer.recognize_google(command_audio, language='en-US')
                                print(f"📝 Command: {command_text}")
                                self.log(f"Voice command: {command_text}")
                                
                                # Process the command
                                self.process_command(command_text.lower())
                                
                            except sr.WaitTimeoutError:
                                self.speak("I didn't hear a command")
                            except sr.UnknownValueError:
                                self.speak("I didn't understand that")
                            except Exception as e:
                                self.speak(f"Error processing command")
                            
                            self.is_listening = False
                        
                        # Direct commands without wake word (for quick access)
                        elif any(word in text.lower() for word in ['open', 'search', 'time', 'date', 'status']):
                            self.process_command(text.lower())
                            self.log(f"Direct command: {text}")
                    
                    except sr.UnknownValueError:
                        pass  # Silent ignore
                    except sr.RequestError:
                        pass
                    
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"Error: {e}")
                    continue
    
    def process_command(self, command):
        """Process command with AI"""
        if not command:
            return
        
        self.log(f"Processing: {command}")
        
        # Special commands
        if 'exit' in command or 'goodbye' in command or 'quit' in command:
            self.speak(self.ai.get_farewell())
            self.log("Shutdown by user")
            self.running = False
            return
        
        # Check for joke/motivation
        if 'joke' in command or 'funny' in command:
            joke = self.ai.tell_joke()
            self.speak(joke)
            return
        
        if 'motivate' in command or 'quote' in command:
            quote = self.ai.get_motivation()
            self.speak(quote)
            return
        
        # Try to execute as system command first
        executed = self.execute_action(command)
        if executed:
            return
        
        # If not a system command, send to AI
        self.speak("Let me think about that...")
        ai_response = self.ai.process_command(command)
        
        # Extract if AI wants to execute something
        extracted = self.ai.extract_command(ai_response)
        
        if extracted['type'] == 'action':
            # AI wants to execute
            self.speak(extracted['response'])
            self.execute_action(extracted['action'])
        else:
            # Just speak AI response
            self.speak(extracted['response'])
    
    def run_voice_mode(self):
        """Main voice mode loop"""
        self.greet()
        
        try:
            self.listen_continuously()
        except KeyboardInterrupt:
            self.speak("Shutting down. Goodbye boss!")
        except Exception as e:
            print(f"Error: {e}")
            self.speak("An error occurred. Restarting...")

if __name__ == "__main__":
    try:
        jarvis = Jarvis()
        jarvis.run_voice_mode()
    except KeyboardInterrupt:
        print("\n👋 JARVIS shut down")
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        with open('logs/error.log', 'a') as f:
            f.write(f"{datetime.now()}: {str(e)}\n")