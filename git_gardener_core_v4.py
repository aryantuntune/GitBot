"""
Git Gardener V4 - Launcher
"""
import tkinter as tk
import os
import sys
import sv_ttk

# Ensure we can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot_ui import ModernApp

if __name__ == "__main__":
    root = tk.Tk()
    
    # Try to apply sun valley theme if available, else standard
    try:
        sv_ttk.set_theme("dark")
    except:
        pass
        
    app = ModernApp(root)
    root.mainloop()
