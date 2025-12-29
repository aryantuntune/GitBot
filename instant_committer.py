
import os
import subprocess
import time
import datetime

# Configuration
REPO_PATH = "."
TARGET_FILE = "output/projects/instant_activity/log.txt"
COMMIT_COUNT = 19

def run_cmd(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=REPO_PATH, stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

print(f"[*] Starting Instant Activity Generator...")
print(f"[*] Target: {COMMIT_COUNT} commits")

# Ensure dir exists
abs_path = os.path.abspath(TARGET_FILE)
os.makedirs(os.path.dirname(abs_path), exist_ok=True)

# Git Pull first
print("[*] Syncing repo...")
run_cmd("git pull --rebase origin master")

for i in range(1, COMMIT_COUNT + 1):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(abs_path, "a") as f:
        f.write(f"Activity Log #{i}: {timestamp}\n")
    
    # Git Add (Absolute Path) - CRITICAL FIX
    abs_path_clean = abs_path.replace("\\", "/")
    run_cmd(f'git add --force "{abs_path_clean}"')
    
    # Git Commit
    if run_cmd(f'git commit -m "chore: instant activity bump {i}/{COMMIT_COUNT}"'):
        print(f" [OK] Commit {i}/{COMMIT_COUNT}")
    else:
        print(f" [!!] Commit {i} failed")
    
    # Optional: fast push every 5 to avoid huge batch issues? 
    # User asked for instant. pushing at end is faster total time.
    time.sleep(0.5)

print("[*] Pushing to remote...")
if run_cmd("git push"):
    print("[SUCCESS] All commits pushed!")
else:
    print("[ERROR] Push failed.")
