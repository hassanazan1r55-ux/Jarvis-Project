import random

class PersonalityManager:
    def __init__(self, mode="friendly"):
        self.mode = mode  # "professional", "friendly", "funny", "strict", "emotional"
        
        self.responses = {
            "professional": {
                "greeting": ["Good morning, sir.", "Good afternoon, sir.", "Good evening, sir."],
                "farewell": ["Goodbye.", "Have a productive day.", "See you later."],
                "acknowledge": ["Understood.", "Proceeding.", "As you wish."],
                "error": ["Apologies, I couldn't process that.", "An error occurred."],
                "think": ["Processing your request...", "Analyzing..."],
                "yes": ["Yes, sir.", "Certainly.", "Absolutely."],
                "no": ["I'm afraid not.", "Negative.", "Unfortunately not."]
            },
            "friendly": {
                "greeting": ["Hey boss! 👋", "Hi there! 😊", "Hello! How are you?", "Good to see you!"],
                "farewell": ["Catch you later! 👋", "See ya!", "Take care!", "Bye bye!"],
                "acknowledge": ["Got it! 👌", "Awesome!", "Sweet!", "Cool!"],
                "error": ["Oops! Something went wrong.", "My bad! Let me try again."],
                "think": ["Hmm, let me think... 🤔", "Interesting! Let me process that..."],
                "yes": ["Yes!", "Totally!", "For sure!", "You bet!"],
                "no": ["Nope!", "Not really.", "I don't think so."]
            },
            "funny": {
                "greeting": ["What's up, boss! 🎉", "Yo! Ready to rock?", "Here we go again! 😂"],
                "farewell": ["See ya later, alligator! 🐊", "Bye bye, boss! 👋"],
                "acknowledge": ["Boom! 💥", "Nice!", "Savage!", "Bet!"],
                "error": ["Well, that backfired! 😅", "Houston, we have a problem!"],
                "think": ["Let me put my thinking cap on... 🎩", "Brain cells loading... 🧠"],
                "yes": ["Duh!", "Obviously!", "You know it!"],
                "no": ["Hard pass!", "Negative, ghost rider!"]
            },
            "strict": {
                "greeting": ["Hello.", "State your request.", "Proceed."],
                "farewell": ["Dismissed.", "Leave.", "That's all."],
                "acknowledge": ["Acknowledged.", "Proceeding.", "Done."],
                "error": ["Error. Try again.", "Failure. Retry."],
                "think": ["Analyzing...", "Computing..."],
                "yes": ["Affirmative.", "Confirmed.", "Approved."],
                "no": ["Denied.", "Negative.", "Rejected."]
            },
            "emotional": {
                "greeting": ["Good morning, my friend! 😊", "How are you today? 💕"],
                "farewell": ["Take care of yourself! 💕", "Stay safe! 🌟"],
                "acknowledge": ["I appreciate that!", "Thank you for telling me!"],
                "error": ["I'm sorry, I couldn't process that. 😢"],
                "think": ["Let me think about this... 💭", "Give me a moment... ⏳"],
                "yes": ["I agree!", "That's wonderful!", "I'm happy about that!"],
                "no": ["I'm afraid not.", "That might not be best."]
            }
        }
    
    def change_mode(self, mode):
        """Change personality mode"""
        if mode in self.responses:
            self.mode = mode
            return f"✅ Switched to {mode} mode!"
        return f"❌ Mode '{mode}' not available. Options: {list(self.responses.keys())}"
    
    def get_response(self, response_type):
        """Get random response of specific type"""
        if response_type in self.responses[self.mode]:
            return random.choice(self.responses[self.mode][response_type])
        return "Hello!"
    
    def get_greeting(self):
        return self.get_response("greeting")
    
    def get_farewell(self):
        return self.get_response("farewell")
    
    def get_acknowledge(self):
        return self.get_response("acknowledge")
    
    def get_error(self):
        return self.get_response("error")
    
    def get_think(self):
        return self.get_response("think")
    
    def get_yes(self):
        return self.get_response("yes")
    
    def get_no(self):
        return self.get_response("no")