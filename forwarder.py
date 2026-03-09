"""
🟠 ORANGE ANALYTICS BOT — FULL INTEGRATED VERSION
Premium • Clean • Charts • Dashboard • Weekly Report • Confidence AI
"""

import re
import os
import asyncio
import hashlib
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from telethon import TelegramClient, events

# =========================================================
# 🔧 CONFIGURATION
# =========================================================

API_ID = 38957368
API_HASH =("ebc59f4e107ed07c65f4bf081b8d88fd")

SOURCE_CHATS = [-1001329677889]   # 🔁 replace
TARGET_CHATS = ['orangeprediction']   # 🔁 replace

BRAND_TAG = "\n\n🔥 Powered by Orange"

# Dark theme charts
plt.style.use("dark_background")

client = TelegramClient("orange_session", API_ID, API_HASH)

# =========================================================
# 📊 GLOBAL STATE
# =========================================================

sent_hashes = set()
forwarded_count = 0
promo_skipped = 0
charts_sent = 0
accuracy = {"correct": 0, "wrong": 0}
last_prediction = None

url_pattern = re.compile(r"http[s]?://\S+|www\.\S+")

# =========================================================
# 🚫 PROMO FILTER
# =========================================================

def is_promotional(text):
    text = text.lower()
    keywords = [
        "create id","whatsapp","deposit","withdraw","bonus",
        "casino","join now","register","online id"
    ]
    if any(k in text for k in keywords):
        return True
    if "http://" in text or "https://" in text or "www." in text:
        return True
    if re.search(r"\+?\d{10,}", text):
        return True
    return False

# =========================================================
# 🧹 CLEAN TEXT
# =========================================================

def clean_text(text):
    text = url_pattern.sub("", text)
    lines = text.split("\n")
    blocked = ["yuvraj singh rajput", "@yuvrajsinh7", "ysr"]
    return "\n".join([l for l in lines if not any(b in l.lower() for b in blocked)])

# =========================================================
# 📊 CONFIDENCE SCORE
# =========================================================

def get_confidence(p1, p2):
    diff = abs(p1 - p2)
    if diff >= 30:
        return "🟢 High Confidence"
    elif diff >= 15:
        return "🟡 Medium Confidence"
    return "🔴 Low Confidence"

# =========================================================
# 📊 GLOBAL STORAGE
# =========================================================

def save_prediction(team1, team2, p1, p2):
    file = "global_predictions.json"
    record = {
        "team1": team1,
        "team2": team2,
        "p1": p1,
        "p2": p2,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    data = []
    if os.path.exists(file):
        with open(file) as f:
            data = json.load(f)
    data.append(record)
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# =========================================================
# 📊 CHARTS
# =========================================================

def extract_probabilities(text):
    m = re.findall(r"([A-Za-z]+)\s*(\d+)%", text)
    if len(m) >= 2:
        return m[0][0], m[1][0], int(m[0][1]), int(m[1][1])
    return None

def create_prediction_chart(team1, team2, p1, p2):
    plt.figure(figsize=(6,6))
    plt.pie([p1, p2], labels=[team1, team2], autopct='%1.1f%%')
    plt.title("Win Probability")
    plt.savefig("prediction_chart.png")
    plt.close()
    return "prediction_chart.png"

def create_accuracy_chart():
    plt.figure(figsize=(6,6))
    plt.pie([accuracy["correct"], accuracy["wrong"]],
            labels=["Correct","Wrong"], autopct='%1.1f%%')
    plt.title("Prediction Accuracy")
    plt.savefig("accuracy_chart.png")
    plt.close()
    return "accuracy_chart.png"

# =========================================================
# 📊 DASHBOARDS
# =========================================================

async def send_daily_dashboard():
    report = f"""
📊 ORANGE DAILY DASHBOARD

📩 Forwarded: {forwarded_count}
🚫 Promo Skipped: {promo_skipped}
📊 Charts Sent: {charts_sent}
📈 Accuracy: {accuracy['correct']}✔ / {accuracy['wrong']}✖

🔥 Powered by Orange
"""
    for t in TARGET_CHATS:
        await client.send_message(t, report)

async def send_weekly_report():
    report = f"""
📊 ORANGE WEEKLY REPORT

📩 Forwarded: {forwarded_count}
📊 Charts Sent: {charts_sent}
📈 Accuracy: {accuracy['correct']}✔ / {accuracy['wrong']}✖

🔥 Powered by Orange
"""
    for t in TARGET_CHATS:
        await client.send_message(t, report)

# =========================================================
# 📩 MESSAGE HANDLER
# =========================================================

@client.on(events.NewMessage(chats=SOURCE_CHATS))
async def handler(event):
    global forwarded_count, promo_skipped, charts_sent, last_prediction

    text = event.raw_text or ""

    # 🚫 Skip videos & GIFs
    if event.message.video or event.message.gif:
        return

    if not text and not event.message.media:
        return

    # 🚫 Promo filter
    if text and is_promotional(text):
        promo_skipped += 1
        return

    # 🚫 Duplicate
    if text:
        h = hashlib.md5(text.encode()).hexdigest()
        if h in sent_hashes:
            return

    # 🎯 Result detection
    if text.lower().startswith("result:"):
        result_team = text.split(":")[1].strip()
        if last_prediction:
            if result_team.lower() == last_prediction.lower():
                accuracy["correct"] += 1
            else:
                accuracy["wrong"] += 1
            chart = create_accuracy_chart()
            for t in TARGET_CHATS:
                await client.send_file(t, chart)
        return

    cleaned = clean_text(text)
    formatted = f"🏏 MATCH UPDATE\n{cleaned}{BRAND_TAG}"

    for t in TARGET_CHATS:
        if event.message.media:
            await client.send_file(t, event.message.media, caption=formatted)
        else:
            await client.send_message(t, formatted)

    forwarded_count += 1
    if text:
        sent_hashes.add(hashlib.md5(text.encode()).hexdigest())

    # 📊 Prediction detection
    parsed = extract_probabilities(text)
    if parsed:
        team1, team2, p1, p2 = parsed
        last_prediction = team1 if p1 > p2 else team2
        save_prediction(team1, team2, p1, p2)

        confidence = get_confidence(p1, p2)

        chart = create_prediction_chart(team1, team2, p1, p2)
        for t in TARGET_CHATS:
            await client.send_file(t, chart)

        charts_sent += 1

# =========================================================
# ⏰ SCHEDULERS
# =========================================================

async def daily_scheduler():
    while True:
        now = datetime.now()
        next_run = (now.replace(hour=0, minute=0, second=0, microsecond=0)
                    + timedelta(days=1))
        await asyncio.sleep((next_run - now).total_seconds())
        await send_daily_dashboard()

async def weekly_scheduler():
    while True:
        now = datetime.now()
        days_until_sunday = (6 - now.weekday()) % 7
        next_run = now + timedelta(days=days_until_sunday)
        next_run = next_run.replace(hour=21, minute=0, second=0, microsecond=0)
        await asyncio.sleep((next_run - now).total_seconds())
        await send_weekly_report()

# =========================================================
# ▶️ RUNNER
# =========================================================

async def run_bot():
    await client.start()
    asyncio.create_task(daily_scheduler())
    asyncio.create_task(weekly_scheduler())
    print("🚀 Orange Analytics Bot Running...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(run_bot())

