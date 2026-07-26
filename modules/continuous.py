"""
Continuous Conversation Module
Handles proactive and continuous chat features
"""

import random
import datetime
import threading
import time

class ContinuousConversation:
    def __init__(self, ai_manager, speak_function):
        self.ai = ai_manager
        self.speak = speak_function
        self.active = False
        self.proactive = False
        self.thread = None
        
        # Proactive topics
        self.topics = [
            "How are you doing today? 😊",
            "Is there anything else I can help you with? 💡",
            "I'm here if you need anything! 🤖",
            "What would you like to do next? 🚀",
            "Have you had a productive day? ⭐"
        ]
    
    def start(self):
        """Start continuous conversation mode"""
        self.active = True
        self.speak("🎯 Continuous conversation mode activated!")
        self.speak("I'll keep the conversation going. Just talk to me naturally!")
        
        if not self.thread or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop continuous conversation mode"""
        self.active = False
        self.proactive = False
        self.speak("🔄 Exiting continuous conversation mode")
    
    def _run(self):
        """Background thread for proactive engagement"""
        while self.active:
            time.sleep(10)  # Check every 10 seconds
            
            # Don't interrupt if user was just talking
            if self.ai.last_interaction:
                time_since = (datetime.datetime.now() - self.ai.last_interaction).seconds
                if time_since > 15:  # 15 seconds of silence
                    self.proactive = True
                    topic = random.choice(self.topics)
                    self.speak(topic)
                    self.proactive = False