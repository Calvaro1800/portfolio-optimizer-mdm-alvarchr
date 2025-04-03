import schedule
import time
import subprocess
from datetime import datetime

LOG_PATH = "logs/auto.log"

def log(message):
    with open(LOG_PATH, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def run_gainers():
    log("🔄 Updating Top Gainers...")
    subprocess.run(["python3", "update_gainers.py"])

def run_news():
    log("📰 Updating News & Sentiment...")
    subprocess.run(["python3", "update_news.py"])

# Schedule tasks
schedule.every(5).minutes.do(run_gainers)
schedule.every(15).minutes.do(run_news)

log("✅ Scheduler started: Gainers every 5 min, News every 15 min")

while True:
    schedule.run_pending()
    time.sleep(1)
