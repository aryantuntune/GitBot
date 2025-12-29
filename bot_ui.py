"""
bot_ui.py - Git Gardener V4 User Interface
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import queue
import threading
import bot_core

class ModernApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Git Gardener V4 🌿")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")
        
        self.bot = bot_core.GitGardener()
        self.setup_styles()
        self.create_widgets()
        
        # Start UI Update Loop
        self.update_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        bg_dark = "#1e1e1e"
        fg_light = "#d4d4d4"
        accent = "#007acc"
        
        style.configure("TFrame", background=bg_dark)
        style.configure("TLabel", background=bg_dark, foreground=fg_light, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#4ec9b0")
        style.configure("Status.TLabel", font=("Segoe UI", 12, "bold"))
        
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8, background="#333", foreground="white")
        style.map("TButton", background=[('active', accent)])
        
        style.configure("TEntry", fieldbackground="#333", foreground="white", padding=5)

    def create_widgets(self):
        # Main Container
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Label(main_frame, text="Git Gardener V4", style="Header.TLabel")
        header.pack(anchor="w", pady=(0, 20))
        
        # Status Section
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.lbl_status = ttk.Label(self.status_frame, text="⚪ READY", style="Status.TLabel", foreground="gray")
        self.lbl_status.pack(side=tk.LEFT)
        
        self.btn_start = ttk.Button(self.status_frame, text="▶ START", command=self.start_bot)
        self.btn_start.pack(side=tk.RIGHT, padx=5)
        
        self.btn_stop = ttk.Button(self.status_frame, text="⏹ STOP", command=self.stop_bot, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.RIGHT, padx=5)

        # Settings Section (Collapsible-ish)
        settings_frame = ttk.LabelFrame(main_frame, text="Configuration", padding=10)
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Grid layout for inputs
        ttk.Label(settings_frame, text="Gemini API Key:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.ent_key = ttk.Entry(settings_frame, width=40)
        self.ent_key.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.ent_key.insert(0, self.bot.config.get("gemini_key", ""))
        
        ttk.Label(settings_frame, text="Ollama Model:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.ent_model = ttk.Entry(settings_frame, width=20)
        self.ent_model.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.ent_model.insert(0, self.bot.config.get("model", "qwen2.5-coder:7b"))

        settings_frame.columnconfigure(1, weight=1)
        
        # Log Area
        ttk.Label(main_frame, text="Live Activity Log").pack(anchor="w", pady=(0, 5))
        
        self.log_area = scrolledtext.ScrolledText(
            main_frame, height=15, 
            bg="#252526", fg="#d4d4d4",
            font=("Consolas", 10),
            state='disabled'
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        # Tags for log coloring
        self.log_area.tag_config("System", foreground="#6a9955")
        self.log_area.tag_config("Gemini", foreground="#c586c0")
        self.log_area.tag_config("Ollama", foreground="#4ec9b0")
        self.log_area.tag_config("Git", foreground="#ce9178")
        self.log_area.tag_config("Error", foreground="#f44747")
        self.log_area.tag_config("CRITICAL", foreground="#f44747", background="#3c1e1e")

    def log(self, role, message, time):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"[{time}] ", "Time")
        self.log_area.insert(tk.END, f"{role}: ", role)
        self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def update_ui(self):
        # Process log queue
        while not self.bot.log_queue.empty():
            entry = self.bot.log_queue.get()
            self.log(entry["role"], entry["message"], entry["time"])
            
            # Check for critical stop
            if entry["message"] == "Bot Stopped":
                self.set_stopped_state()

        # Update status visuals
        if self.bot.running:
             pass # Animation logic could go here
             
        self.root.after(100, self.update_ui)

    def start_bot(self):
        # Save config first
        new_config = {
            "gemini_key": self.ent_key.get(),
            "model": self.ent_model.get()
        }
        self.bot.save_config(new_config)
        
        if not new_config["gemini_key"]:
            messagebox.showerror("Error", "Please enter a Gemini API Key")
            return

        self.bot.start()
        self.set_running_state()

    def stop_bot(self):
        self.bot.stop()
        self.btn_stop.config(text="STOPPING...", state=tk.DISABLED)

    def set_running_state(self):
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL, text="⏹ STOP")
        self.lbl_status.config(text="🟢 RUNNING", foreground="#4caf50")
        self.ent_key.config(state=tk.DISABLED)
        self.ent_model.config(state=tk.DISABLED)

    def set_stopped_state(self):
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED, text="⏹ STOP")
        self.lbl_status.config(text="⚪ STOPPED", foreground="gray")
        self.ent_key.config(state=tk.NORMAL)
        self.ent_model.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernApp(root)
    root.mainloop()
