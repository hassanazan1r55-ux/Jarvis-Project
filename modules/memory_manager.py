import json
import os
from datetime import datetime
from pathlib import Path

class MemoryManager:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.data_dir.mkdir(exist_ok=True)
        
        self.memory_file = self.data_dir / 'memory.json'
        self.history_file = self.data_dir / 'history.json'
        self.tasks_file = self.data_dir / 'tasks.json'
        self.habits_file = self.data_dir / 'habits.json'
        
        self.memory = self._load_json(self.memory_file)
        self.history = self._load_json(self.history_file)
        self.tasks = self._load_json(self.tasks_file)
        self.habits = self._load_json(self.habits_file)
        
        # Default memory structure
        if not self.memory:
            self.memory = {
                "user_name": None,
                "user_preferences": {
                    "favorite_apps": [],
                    "default_browser": "chrome",
                    "morning_person": True,
                    "language": "english",
                    "voice_speed": 170
                },
                "conversation_context": [],
                "last_interaction": None
            }
            self._save_json(self.memory_file, self.memory)
    
    def _load_json(self, file_path):
        """Load JSON file"""
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_json(self, file_path, data):
        """Save JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    # ============================================
    # USER MEMORY
    # ============================================
    
    def remember_user(self, key, value):
        """Remember user information"""
        if key == "name":
            self.memory["user_name"] = value
        elif key in self.memory["user_preferences"]:
            self.memory["user_preferences"][key] = value
        else:
            self.memory[key] = value
        
        self._save_json(self.memory_file, self.memory)
        return f"✅ Remembered: {key} = {value}"
    
    def get_user_info(self, key):
        """Get user information"""
        if key == "name":
            return self.memory.get("user_name")
        elif key in self.memory.get("user_preferences", {}):
            return self.memory["user_preferences"].get(key)
        return self.memory.get(key)
    
    def get_all_user_info(self):
        """Get all user info"""
        info = f"User: {self.memory.get('user_name', 'Unknown')}\n"
        info += "Preferences:\n"
        for key, value in self.memory.get("user_preferences", {}).items():
            info += f"  - {key}: {value}\n"
        return info
    
    # ============================================
    # CONVERSATION HISTORY
    # ============================================
    
    def add_to_history(self, user_message, jarvis_response):
        """Add conversation to history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "jarvis": jarvis_response
        }
        
        if isinstance(self.history, list):
            self.history.append(entry)
        else:
            self.history = [entry]
        
        # Keep last 100 conversations
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        self._save_json(self.history_file, self.history)
    
    def get_recent_context(self, limit=5):
        """Get recent conversation context"""
        if isinstance(self.history, list) and len(self.history) > 0:
            recent = self.history[-limit:]
            context = "\n".join([
                f"User: {h['user']}\nJARVIS: {h['jarvis']}"
                for h in recent
            ])
            return context
        return None
    
    def get_conversation_by_keyword(self, keyword):
        """Search conversation by keyword"""
        if not isinstance(self.history, list):
            return None
        
        results = []
        for h in self.history:
            if keyword.lower() in h['user'].lower() or keyword.lower() in h['jarvis'].lower():
                results.append(h)
        
        return results
    
    # ============================================
    # TASK MEMORY
    # ============================================
    
    def add_task(self, task, time=None, date=None):
        """Add a new task"""
        task_entry = {
            "id": len(self.tasks) + 1 if isinstance(self.tasks, list) else 1,
            "task": task,
            "time": time,
            "date": date,
            "completed": False,
            "created": datetime.now().isoformat()
        }
        
        if isinstance(self.tasks, list):
            self.tasks.append(task_entry)
        else:
            self.tasks = [task_entry]
        
        self._save_json(self.tasks_file, self.tasks)
        return f"✅ Task added: {task} at {time if time else 'unscheduled time'}"
    
    def get_pending_tasks(self):
        """Get all pending tasks"""
        if not isinstance(self.tasks, list):
            return []
        
        return [t for t in self.tasks if not t.get("completed", False)]
    
    def complete_task(self, task_id):
        """Mark task as completed"""
        if not isinstance(self.tasks, list):
            return "No tasks found"
        
        for task in self.tasks:
            if task.get("id") == task_id:
                task["completed"] = True
                self._save_json(self.tasks_file, self.tasks)
                return f"✅ Task completed: {task['task']}"
        
        return "❌ Task not found"
    
    def get_tasks_by_time(self, time):
        """Get tasks at specific time"""
        if not isinstance(self.tasks, list):
            return []
        
        return [t for t in self.tasks if t.get("time") == time and not t.get("completed", False)]
    
    # ============================================
    # HABITS TRACKING
    # ============================================
    
    def add_habit(self, habit, time=None, frequency="daily"):
        """Add a new habit"""
        habit_entry = {
            "habit": habit,
            "time": time,
            "frequency": frequency,
            "streak": 0,
            "last_completed": None,
            "active": True
        }
        
        if isinstance(self.habits, list):
            self.habits.append(habit_entry)
        else:
            self.habits = [habit_entry]
        
        self._save_json(self.habits_file, self.habits)
        return f"✅ Habit added: {habit} at {time if time else 'unscheduled time'}"
    
    def get_habits_by_time(self, time):
        """Get habits at specific time"""
        if not isinstance(self.habits, list):
            return []
        
        return [h for h in self.habits if h.get("time") == time and h.get("active", True)]
    
    def complete_habit(self, habit_name):
        """Mark habit as completed today"""
        if not isinstance(self.habits, list):
            return "No habits found"
        
        for habit in self.habits:
            if habit.get("habit").lower() == habit_name.lower():
                habit["streak"] = habit.get("streak", 0) + 1
                habit["last_completed"] = datetime.now().isoformat()
                self._save_json(self.habits_file, self.habits)
                return f"✅ Great! {habit_name} streak: {habit['streak']} days"
        
        return "❌ Habit not found"
    
    # ============================================
    # CONTEXT AWARENESS
    # ============================================
    
    def update_context(self, topic, sentiment="neutral"):
        """Update conversation context"""
        self.memory["conversation_context"].append({
            "topic": topic,
            "sentiment": sentiment,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep last 10 contexts
        if len(self.memory["conversation_context"]) > 10:
            self.memory["conversation_context"] = self.memory["conversation_context"][-10:]
        
        self._save_json(self.memory_file, self.memory)
    
    def get_current_context(self):
        """Get current conversation context"""
        context = self.memory.get("conversation_context", [])
        if context:
            last = context[-1]
            return f"Last topic: {last['topic']}, Sentiment: {last['sentiment']}"
        return None
    
    # ============================================
    # DAILY ROUTINE
    # ============================================
    
    def get_daily_routine(self):
        """Get daily routine based on time"""
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            return {
                "time": "morning",
                "actions": ["wake up", "morning routine", "check schedule"],
                "suggestions": ["Good morning! Ready to start the day?"]
            }
        elif 12 <= current_hour < 17:
            return {
                "time": "afternoon",
                "actions": ["lunch", "meetings", "work"],
                "suggestions": ["Don't forget lunch!"]
            }
        elif 17 <= current_hour < 21:
            return {
                "time": "evening",
                "actions": ["winding down", "dinner", "relax"],
                "suggestions": ["Evening routine time!"]
            }
        else:
            return {
                "time": "night",
                "actions": ["sleep", "prepare for tomorrow"],
                "suggestions": ["Good night! Sleep well!"]
            }