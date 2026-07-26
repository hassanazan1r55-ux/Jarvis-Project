import os
import datetime
import psutil
import pyautogui
import subprocess
import json

class SystemManager:
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        with open('config.json', 'r') as f:
            return json.load(f)
    
    def get_time(self):
        return datetime.datetime.now().strftime("%I:%M %p")
    
    def get_date(self):
        return datetime.datetime.now().strftime("%B %d, %Y")
    
    def get_system_status(self):
        battery = psutil.sensors_battery()
        battery_info = {
            'percent': battery.percent if battery else 0,
            'plugged': battery.power_plugged if battery else False
        }
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        return {
            'battery': battery_info,
            'cpu': cpu,
            'ram': ram
        }
    
    def take_screenshot(self):
        try:
            screenshot = pyautogui.screenshot()
            filename = f"logs/screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot.save(filename)
            return f"Screenshot saved: {filename}"
        except Exception as e:
            return f"Screenshot failed: {str(e)}"
    
    def open_app(self, app_name):
        try:
            apps = self.config.get('APPS', {})
            if app_name in apps:
                os.startfile(apps[app_name])
            else:
                subprocess.Popen(app_name)
            return f"Opening {app_name}"
        except:
            return f"Failed to open {app_name}"
    
    def close_app(self, app_name):
        try:
            os.system(f"taskkill /f /im {app_name}.exe")
            return f"Closed {app_name}"
        except:
            return f"Failed to close {app_name}"
    
    def shutdown_system(self):
        os.system("shutdown /s /t 5")
        return "System shutting down in 5 seconds"
    
    def restart_system(self):
        os.system("shutdown /r /t 5")
        return "System restarting in 5 seconds"
    
    def lock_system(self):
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return "System locked"