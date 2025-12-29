# 🌿 Git Gardener Bot - Setup Guide

**An intelligent bot that automatically maintains your GitHub contribution graph**

---

## 🎯 What Does This Bot Do?

- Generates real Python projects using AI (Gemini + Ollama)
- Commits code to your GitHub repository automatically
- Runs in the background 24/7
- Only works when your PC is idle (won't slow you down)
- Respects daily commit limits
- Starts automatically when you turn on your PC

---

## 📋 Prerequisites

Before you start, make sure you have:

1. **Python 3.8+** installed ([Download here](https://www.python.org/downloads/))
   - During installation, check "Add Python to PATH"
   
2. **Ollama** installed and running ([Download here](https://ollama.ai/download))
   - After installing, open a terminal and run: `ollama pull qwen2.5-coder:7b`
   
3. **Git** installed ([Download here](https://git-scm.com/downloads))

4. **A Gemini API Key** (Free!)
   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Click "Create API Key"
   - Copy the key (you'll need it in Step 3)

5. **A GitHub Repository**
   - Create a new empty repository on GitHub
   - Copy the repository URL (e.g., `https://github.com/yourusername/your-repo.git`)

---

## 🚀 Setup Instructions (5 Minutes)

### Step 1: Download the Bot
- Download this entire folder to your PC
- Extract it somewhere permanent (e.g., `C:\GitBot\` or `D:\GitBot\`)
- **Don't put it in Downloads or Desktop** - it needs to stay in one place

### Step 2: Initialize Git Repository
1. Open the bot folder in File Explorer
2. Right-click and select "Open in Terminal" (or "Git Bash Here")
3. Run these commands:
   ```bash
   git init
   git remote add origin YOUR_GITHUB_REPO_URL
   ```
   Replace `YOUR_GITHUB_REPO_URL` with your actual repository URL

### Step 3: Configure the Bot
1. Double-click `settings_gui.bat`
2. A window will open - fill in:
   - **Gemini API Key**: Paste the key from Google AI Studio
   - **Ollama Model**: Leave as `qwen2.5-coder:7b` (or change if you installed a different model)
   - **Interval**: How many seconds to wait between commits (default: 60)
   - **Max Commits**: Daily limit (default: 20)
   - **Repo URL**: Your GitHub repository URL
   - **Name**: Your name (for Git commits)
   - **Email**: Your email (for Git commits)
3. Click "Save" or close the window (settings auto-save)

### Step 4: Start the Bot (One Time Only!)
1. Double-click `start_agent.bat`
2. You'll see a message: "Bot is now running in the background!"
3. **Close the window** - the bot keeps running
4. You should get a Windows notification: "Git Gardener Started"

**That's it!** The bot is now running and will start automatically every time you turn on your PC.

---

## 📱 How to Use

### Daily Operation
- **Nothing!** The bot runs automatically in the background
- You'll get notifications when:
  - The bot starts
  - Daily commit limit is reached
  - Any errors occur

### To Change Settings
- Double-click `settings_gui.bat`
- Make your changes
- Close the window
- The bot automatically uses the new settings

### To Stop the Bot
- Double-click `kill_switch.bat`
- You'll get a notification: "Bot has been terminated"

### To Restart the Bot
- Double-click `start_agent.bat` again

---

## 🔧 Important Files

| File | Purpose |
|------|---------|
| `start_agent.bat` | Starts the bot (run once, auto-starts on boot) |
| `settings_gui.bat` | Opens settings window |
| `kill_switch.bat` | Stops the bot completely |
| `bot_config.json` | Your settings (API keys, limits, etc.) |
| `instant_committer.py` | Optional: Run `python instant_committer.py` for 20 instant commits |

---

## 🎨 How It Works

1. **Idle Detection**: The bot monitors your CPU usage
   - If you're busy (gaming, working), it waits
   - When your PC is idle, it starts generating code

2. **Project Generation**:
   - Gemini AI creates project ideas
   - Ollama generates the actual Python code
   - Code is committed to your GitHub repo

3. **Smart Scheduling**:
   - Respects daily commit limits
   - Spreads commits throughout the day
   - Keeps a detailed log of all AI conversations

---

## ❓ Troubleshooting

### "Gemini API Key is missing" notification
- Run `settings_gui.bat` and add your API key
- Make sure you enabled the Generative Language API in Google Cloud Console

### Bot not committing to GitHub
- Check that Git is configured: `git config --global user.name "Your Name"`
- Make sure you added the remote: `git remote -v`
- Verify you have push access to the repository

### Ollama errors
- Make sure Ollama is running: Open a terminal and type `ollama list`
- If the model isn't installed: `ollama pull qwen2.5-coder:7b`

### Bot not starting on boot
- Press `Win + R`, type `shell:startup`, press Enter
- Check if `GitGardenerAgent.lnk` exists
- If not, run `start_agent.bat` again

---

## 🛡️ Privacy & Security

- **Your API keys stay on your PC** - they're stored in `bot_config.json`
- **Credentials are NEVER committed to Git** - `bot_config.json` is in `.gitignore`
- The bot only commits to YOUR repository
- All code generation happens locally (via Ollama)
- Gemini is only used for project ideas and file planning

### Important Security Notes:
✅ `bot_config.json` (contains your API keys) is **automatically excluded** from Git commits
✅ When sharing this bot with friends, they'll use `bot_config.json.template` to create their own config
✅ Your Gemini API key is only used for API calls - it never leaves your machine
✅ The bot only has access to the repository you configure

**Safe to share:**
- The entire bot folder (except `bot_config.json`)
- Your friends will create their own `bot_config.json` with their own API keys

**Never share:**
- Your `bot_config.json` file (contains your API key)

---

## 🎁 Bonus Features

### Instant Activity Boost
Want to fill your contribution graph quickly?
```bash
python instant_committer.py
```
This makes 20 commits in ~30 seconds (use sparingly!)

### View AI Conversations
Open `conversation_transcript.md` to see every interaction between Gemini and Ollama

---

## 📞 Support

If you run into issues:
1. Check `debug.log` for error messages
2. Make sure all prerequisites are installed
3. Verify your API key is valid
4. Ensure Ollama is running

---

## 🎉 You're All Set!

Your GitHub contribution graph will now be automatically maintained. The bot:
- ✅ Runs 24/7 in the background
- ✅ Starts automatically on boot
- ✅ Only works when you're idle
- ✅ Sends notifications for important events
- ✅ Respects daily limits

**Just set it and forget it!** 🚀

---

*Made with ❤️ for developers who want a green contribution graph*
