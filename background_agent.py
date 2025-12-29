
import bot_core
import time
import sys
import os
import subprocess

def send_notification(title, message):
    """Send Windows 10 toast notification."""
    try:
        # Use PowerShell to send Windows notification
        ps_script = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$template = @"
<toast>
    <visual>
        <binding template="ToastText02">
            <text id="1">{title}</text>
            <text id="2">{message}</text>
        </binding>
    </visual>
</toast>
"@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Git Gardener Bot").Show($toast)
'''
        subprocess.run(["powershell", "-Command", ps_script], 
                      capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    except:
        pass  # Fail silently if notifications don't work

def main():
    bot = bot_core.GitGardener()
    
    # Check config
    if not bot.config.get("gemini_key"):
        send_notification("Git Gardener - Error", "Gemini API Key is missing! Please configure.")
        sys.exit(1)
    
    # Notify startup
    send_notification("Git Gardener Started", "Bot is now monitoring and will commit when idle.")
    
    bot.start()
    
    last_count = 0
    
    try:
        while True:
            # Process the log queue (but don't print to console since we're windowless)
            while not bot.log_queue.empty():
                entry = bot.log_queue.get()
                
                # Send notifications for important events
                if "Daily Limit Reached" in entry['message']:
                    if bot.stats.get_count() != last_count:
                        send_notification("Git Gardener - Daily Limit", 
                                        f"Reached {bot.stats.get_count()} commits today. Bot will resume tomorrow.")
                        last_count = bot.stats.get_count()
                
                elif "CRITICAL" in entry['role']:
                    send_notification("Git Gardener - Error", entry['message'][:100])
            
            time.sleep(5)
    except KeyboardInterrupt:
        bot.stop()
        while bot.running:
            time.sleep(0.5)
        send_notification("Git Gardener Stopped", "Bot has been terminated.")

if __name__ == "__main__":
    main()
