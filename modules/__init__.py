# This file makes the modules directory a Python package
# It allows imports like: from modules import system, browser, ai

from .system import SystemManager
from .browser import BrowserManager
from .ai import AIManager

__all__ = ['SystemManager', 'BrowserManager', 'AIManager']