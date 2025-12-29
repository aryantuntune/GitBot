"""
bot_core.py - Git Gardener V4 Core Logic
"""
import os
import json
import time
import datetime
import subprocess
import urllib.request
import urllib.error
import threading
import queue
import re

# --- CONFIGURATION ---
DEFAULT_CONFIG = {
    "gemini_key": "",
    "model": "qwen2.5-coder:7b",
    "interval": 60,
    "max_commits": 20,
    "repo_url": "",
    "name": "GitBot",
    "email": "bot@example.com"
}

class Logger:
    def __init__(self, log_queue):
        self.queue = log_queue

    def log(self, role, message):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.queue.put({"role": role, "message": message, "time": ts})

class GeminiClient:
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, api_key, logger):
        self.api_key = api_key
        self.logger = logger

    def list_models(self):
        url = f"{self.BASE_URL}/models?key={self.api_key}"
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                return [m['name'] for m in data.get('models', []) 
                       if 'generateContent' in m.get('supportedGenerationMethods', [])]
        except Exception as e:
            self.logger.log("Error", f"Failed to list models: {e}")
            return []

    def generate_content(self, prompt, model="models/gemini-1.5-flash"):
        url = f"{self.BASE_URL}/{model}:generateContent?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode('utf-8'))
                if 'candidates' in result and result['candidates']:
                    return result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            self.logger.log("Error", f"Gemini Request Failed: {e}")
        return None

class OllamaClient:
    def __init__(self, model, logger):
        self.model = model
        self.logger = logger
        self.url = "http://localhost:11434/api/generate"

    def generate(self, prompt):
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
             "options": {"num_ctx": 8192}
        }
        try:
            req = urllib.request.Request(
                self.url, 
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=300) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get("response", "")
        except Exception as e:
            self.logger.log("Error", f"Ollama Failed: {e}")
            return None

class GitManager:
    def __init__(self, repo_path, logger, config):
        self.repo_path = repo_path
        self.logger = logger
        self.config = config

    def run(self, cmd):
        try:
            result = subprocess.run(
                cmd, shell=True, check=True, cwd=self.repo_path,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8'
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            # Return combined output for better debugging
            err_msg = f"STDOUT: {e.stdout}\nSTDERR: {e.stderr}"
            return False, err_msg

    def init_repo(self):
        if not os.path.exists(os.path.join(self.repo_path, ".git")):
            self.run("git init")
            self.run(f'git config user.name "{self.config.get("name")}"')
            self.run(f'git config user.email "{self.config.get("email")}"')
            self.logger.log("System", "Git Repository Initialized")

    def commit(self, filename, message):
        # Resolve to absolute path to avoid CWD ambiguity
        abs_path = os.path.abspath(filename)
        # Normalize for git (forward slashes)
        abs_path = abs_path.replace("\\", "/")
        
        # Add validity check
        if not os.path.exists(abs_path):
             self.logger.log("Error", f"File not found: {abs_path}")
             return False

        success_add, out_add = self.run(f'git add --force --verbose "{abs_path}"')
        if not success_add:
             self.logger.log("Error", f"Git Add Failed: {out_add}")
             return False
             
        success, out = self.run(f'git commit -m "{message}"')
        if success:
            self.logger.log("Git", f"Committed: {message}")
            return True
        else:
            self.logger.log("Error", f"Commit Failed: {out}")
            return False

    def push(self):
        if self.config.get("repo_url"):
            self.run(f'git remote add origin {self.config.get("repo_url")}')
            # Pull changes first to avoid conflicts/rejection
            self.run("git pull --rebase origin master")
            
            success, out = self.run("git push -u origin master")
            if success:
                self.logger.log("Git", "Pushed to remote")
            else:
                self.logger.log("Warning", f"Push Failed: {out}")

class DailyStats:
    def __init__(self, filename="daily_stats.json"):
        self.filename = filename

    def get_count(self):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    data = json.load(f)
                    if data.get("date") == today:
                        return data.get("count", 0)
            except: pass
        return 0

    def increment(self):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        count = self.get_count() + 1
        with open(self.filename, "w") as f:
            json.dump({"date": today, "count": count}, f)
        return count

class GitGardener:
    def __init__(self, config_file="bot_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.stats = DailyStats()
        self.log_queue = queue.Queue()
        self.logger = Logger(self.log_queue)
        
        self.running = False
        self.thread = None
        self.stop_event = threading.Event()
        
        self.gemini = None
        self.ollama = None
        self.git = None

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        return DEFAULT_CONFIG

    def save_config(self, new_config):
        self.config = {**self.config, **new_config}
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def start(self):
        if self.running: return
        self.running = True
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.run_loop, daemon=True)
        self.thread.start()
        self.logger.log("System", "Bot Started (V4 Core)")

    def stop(self):
        if not self.running: return
        self.logger.log("System", "Stopping...")
        self.stop_event.set()
        self.running = False

    def log_transcript(self, actor, input_text, output_text):
        """Append detailed interaction to a markdown transcript."""
        try:
            with open("conversation_transcript.md", "a", encoding="utf-8") as f:
                ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n## {ts} - {actor}\n")
                f.write(f"**Input/Prompt:**\n```\n{input_text.strip()}\n```\n")
                f.write(f"**Output/Response:**\n```\n{output_text.strip()}\n```\n")
                f.write("-" * 40 + "\n")
        except: pass

    def is_system_idle(self):
        """Check if system CPU usage is low enough to start heavy tasks."""
        try:
            # wmic is a reliable zero-dep way to get CPU load on Windows
            cmd = "wmic cpu get loadpercentage /value"
            res = subprocess.check_output(cmd, shell=True, encoding='utf-8')
            match = re.search(r"LoadPercentage=(\d+)", res)
            if match:
                load = int(match.group(1))
                threshold = int(self.config.get("idle_threshold", 40))
                is_idle = load < threshold
                if not is_idle:
                    self.logger.log("System", f"System Busy ({load}% CPU). Waiting for idle...")
                return is_idle
        except Exception as e:
            # Fallback to True if check fails (don't block bot forever)
            return True
        return True

    def run_loop(self):
        try:
            self.gemini = GeminiClient(self.config["gemini_key"], self.logger)
            self.ollama = OllamaClient(self.config["model"], self.logger)
            
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Model Selection
            self.logger.log("System", "Connecting to Gemini...")
            all_models = self.gemini.list_models()
            
            PRIORITY_ORDER = [
                "models/gemini-1.5-flash",
                "models/gemini-1.5-flash-latest",
                "models/gemini-1.5-pro",
                "models/gemini-1.5-pro-latest",
                "models/gemini-1.0-pro"
            ]
            
            candidates = [m for m in PRIORITY_ORDER if m in all_models]
            other_flash = [m for m in all_models if 'flash' in m.lower() and m not in candidates]
            other_flash.sort(reverse=True)
            candidates.extend(other_flash)
            candidates.extend([m for m in all_models if m not in candidates])
            if not candidates: candidates = ["models/gemini-1.5-flash"]
            
            current_model_index = 0
            
            # Main Project Loop
            project_path = os.path.join(output_dir, "Daily_Project")
            
            # --- Monorepo Git Init (Root) ---
            # We treat the current directory as the main repo
            self.git = GitManager(".", self.logger, self.config)
            self.git.init_repo() # Init root if needed
            
            consecutive_errors = 0
            
            # --- SUPER LOOP: Indestructible ---
            while not self.stop_event.is_set():
                try: 
                    # --- 1. Daily Limit Check ---
                    current_count = self.stats.get_count()
                    max_commits = int(self.config.get("max_commits", 20))
                    
                    if current_count >= max_commits:
                        self.logger.log("System", f"Daily Limit Reached ({current_count}/{max_commits})")
                        time.sleep(60)
                        continue

                    current_model = candidates[current_model_index]
                    
                    # --- 2. Project State Management ---
                    project_state_file = "current_project.json"
                    current_project = {}
                    if os.path.exists(project_state_file):
                        try:
                            with open(project_state_file, "r") as f:
                                current_project = json.load(f)
                        except: pass
                    
                    # Start New Project? (If none or > 5 files)
                    if not current_project or current_project.get("file_count", 0) >= 5:
                        self.logger.log("Gemini", f"Brainstorming NEW project ({current_model})...")
                        idea_prompt = (
                            "Generate a unique, intermediate-level Python project idea. "
                            "It should be a valid, real-world tool or utility. "
                            "Return JSON: {project_name, folder_name, description}"
                        )
                        idea_resp = self.gemini.generate_content(idea_prompt, current_model)
                        
                        if idea_resp:
                            self.log_transcript("Gemini (Ideation)", idea_prompt, idea_resp)
                            try:
                                json_str = re.search(r'\{.*\}', idea_resp, re.DOTALL)
                                if json_str:
                                    idea = json.loads(json_str.group(0))
                                    today_str = datetime.datetime.now().strftime("%Y%m%d")
                                    safe_name = "".join([c for c in idea.get('folder_name', 'Project') if c.isalnum() or c in ('_','-')])
                                    folder_name = f"{today_str}_{safe_name}"
                                    
                                    current_project = {
                                        "project_name": idea.get("project_name", "Unnamed"),
                                        "folder_name": folder_name,
                                        "description": idea.get("description", "A cool project"),
                                        "file_count": 0,
                                        "files": []
                                    }
                                    with open(project_state_file, "w") as f:
                                        json.dump(current_project, f)
                                    self.logger.log("System", f"New Project: {current_project['project_name']}")
                            except: pass

                    if not current_project:
                        time.sleep(5)
                        continue

                    # Setup Dir ONLY (Git is handled at root now)
                    project_dir = os.path.join(output_dir, "projects", current_project["folder_name"])
                    os.makedirs(project_dir, exist_ok=True)

                    # CRITICAL FIX: Remove nested .git if it exists (force Monorepo)
                    nested_git = os.path.join(project_dir, ".git")
                    if os.path.exists(nested_git):
                        self.logger.log("Warning", f"Removing nested git repo in {current_project['folder_name']}")
                        # Windows specific force remove
                        try:
                            import shutil
                            # Handle read-only files in .git
                            def onerror(func, path, exc_info):
                                import stat
                                if not os.access(path, os.W_OK):
                                    os.chmod(path, stat.S_IWUSR)
                                    func(path)
                                else:
                                    raise
                            shutil.rmtree(nested_git, onerror=onerror)
                        except Exception as e:
                            self.logger.log("Error", f"Failed to remove nested git: {e}")
                    
                    # Generate File
                    context = (
                        f"Project: {current_project['project_name']}\n"
                        f"Description: {current_project['description']}\n"
                        f"Existing Files: {', '.join(current_project.get('files', []))}"
                    )
                    task_prompt = (
                        f"{context}\n"
                        "Suggest the next necessary Python file for this project. "
                        "Return JSON: {filename, description, code_prompt}"
                    )
                    
                    self.logger.log("Gemini", f"Designing next file for {current_project['project_name']}...")
                    response = self.gemini.generate_content(task_prompt, current_model)
                    
                    if not response:
                        # Rotation Logic
                        self.logger.log("Warning", f"Model {current_model} failed. Rotating...")
                        if len(candidates) > 1:
                            current_model_index = (current_model_index + 1) % len(candidates)
                            time.sleep(1)
                            continue
                        else:
                            time.sleep(5)
                            continue
                    
                    self.log_transcript("Gemini (Task)", task_prompt, response)

                    try:
                        json_str = re.search(r'\{.*\}', response, re.DOTALL)
                        if json_str:
                            task = json.loads(json_str.group(0))
                            filename = task.get("filename", "utils.py")
                            desc = task.get("description", "Utility")
                            code_prompt = task.get("code_prompt", "Write code")
                            
                            if filename in current_project.get("files", []):
                                filename = f"v2_{filename}"
                            
                            self.logger.log("System", f"Task: Create {filename}")
                            
                            # --- IDLE CHECK BEFORE HEAVY OLLAMA WORK ---
                            while not self.is_system_idle() and not self.stop_event.is_set():
                                time.sleep(30) # Wait 30s and check again
                            
                            if self.stop_event.is_set(): break

                            self.logger.log("Ollama", "Coding...")
                            
                            full_code = (
                                f"Write complete Python code for '{filename}'.\n"
                                f"Context: {current_project['description']}\n"
                                f"Requirement: {code_prompt}\n"
                                "Return ONLY code."
                            )
                            code = self.ollama.generate(full_code)
                            
                            if code:
                                self.log_transcript("Ollama (Coding)", full_code, code)
                                code = re.sub(r"^`{3,}[a-zA-Z]*\n", "", code.strip())
                                code = re.sub(r"\n`{3,}$", "", code.strip())
                                
                                # Calculate relative path for git add (since git is at root)
                                rel_path = os.path.join("output", "projects", current_project["folder_name"], filename)
                                
                                with open(rel_path, "w") as f:
                                    f.write(code)
                                    
                                if self.git.commit(rel_path, f"feat: {desc}"):
                                    self.git.push() # Push changes to remote
                                    new_count = self.stats.increment()
                                    self.logger.log("System", f"Daily Progress: {new_count}/{max_commits}")
                                    
                                    current_project["file_count"] += 1
                                    current_project["files"].append(filename)
                                    with open(project_state_file, "w") as f:
                                        json.dump(current_project, f)
                                
                                for _ in range(self.config["interval"]):
                                    if self.stop_event.is_set(): break
                                    time.sleep(1)
                            else:
                                self.logger.log("Error", "Ollama produced no code")
                    except Exception as e:
                        self.logger.log("Error", f"Failed to parse task: {e}")
                    
                    if self.stop_event.is_set(): break
                    time.sleep(5)
                    
                except Exception as e:
                    self.logger.log("CRITICAL", f"Safety Loop Error: {e}")
                    import traceback
                    traceback.print_exc()
                    time.sleep(10) # Wait before retry
                
        finally:
            self.logger.log("System", "Bot Stopped")
            self.running = False
