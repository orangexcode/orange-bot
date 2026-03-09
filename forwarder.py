"""
ORANGE ANALYTICS BOT
Forward + Filters + Charts + Prediction Cards
Production Version
"""

import re
import asyncio
import hashlib
import json
import socket
from datetime import datetime

from telethon import TelegramClient, events
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

# =============================
# CONFIG
# =============================

API_ID = 38957368
API_HASH = "ebc59f4e107ed07c65f4bf081b8d88fd"

SOURCE_CHATS = [-1001329677889]
TARGET_CHATS = ['orangeprediction']

BRAND_TAG = "\n\n🔥 Powered by Orange"

# =============================
# TELEGRAM CLIENT
# =============================

client = TelegramClient("orange_session", API_ID, API_HASH)

# =============================
# GLOBAL STATE
# =============================

processed_messages = set()
sent_hashes = set()

# =============================
# PROMO FILTER
# =============================

promo_words = [
    "plum247",
    "plum365",
    "plum999",
    "lordsexch",
    "deposit",
    "whatsapp",
    "create id"
]

remove_words = [
    "yuvraj singh rajput",
    "@yuvrajsinh7"
]

url_pattern = re.compile(r"http[s]?://\S+|www\.\S+")

# =============================
# CLEAN TEXT
# =============================

def clean_text(text):

    text = text.lower()

    for word in remove_words:
        text = text.replace(word, "")

    text = url_pattern.sub("", text)

    return text.strip()

# =============================
# PROMO DETECTOR
# =============================

def is_promo(text):

    text_lower = text.lower()

    for word in promo_words:
        if word in text_lower:
            return True

    return False

# =============================
# PREDICTION CARD
# =============================

def create_prediction_card(match, prediction):

    img = Image.new("RGB", (900, 500), (18,18,18))
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("arial.ttf", 50)
        font_small = ImageFont.truetype("arial.ttf", 35)
    except:
        font_big = None
        font_small = None

    draw.text((40,40), "ORANGE ANALYTICS", fill=(255,140,0), font=font_big)

    draw.text((40,200), "Match:", fill=(255,255,255), font=font_small)
    draw.text((200,200), match, fill=(255,255,255), font=font_small)

    draw.text((40,270), "Prediction:", fill=(255,255,255), font=font_small)
    draw.text((260,270), prediction, fill=(0,255,120), font=font_small)

    draw.text((40,420), "Powered by Orange", fill=(255,140,0), font=font_small)

    filename = "prediction.png"
    img.save(filename)

    return filename

# =============================
# PIE CHART
# =============================

def extract_probabilities(text):

    match = re.findall(r"([A-Za-z]+)\s*(\d+)%", text)

    if len(match) >= 2:
        t1,p1 = match[0]
        t2,p2 = match[1]
        return t1,t2,int(p1),int(p2)

    return None

def create_chart(team1, team2, p1, p2):

    file = "chart.png"

    plt.figure()
    plt.pie([p1,p2], labels=[team1,team2], autopct='%1.1f%%')
    plt.title("Win Probability")
    plt.savefig(file)
    plt.close()

    return file

# =============================
# ANALYTICS
# =============================

def save_analytics(text):

    data = {
        "prediction": text,
        "time": str(datetime.now())
    }

    with open("analytics.json", "a") as f:
        f.write(json.dumps(data) + "\n")

# =============================
# INTERNET CHECK
# =============================

def internet_ok():

    try:
        socket.create_connection(("8.8.8.8",53),5)
        return True
    except:
        return False

# =============================
# MESSAGE HANDLER
# =============================

@client.on(events.NewMessage(chats=SOURCE_CHATS))
async def handler(event):

    msg_id = event.id

    if msg_id in processed_messages:
        return

    processed_messages.add(msg_id)

    if event.video:
        return

    text = event.raw_text or ""

    if not text and not event.message.media:
        return

    if is_promo(text):
        return

    cleaned = clean_text(text)

    msg_hash = hashlib.md5(cleaned.encode()).hexdigest()

    if msg_hash in sent_hashes:
        return

    sent_hashes.add(msg_hash)

    formatted = cleaned + BRAND_TAG

    try:

        for target in TARGET_CHATS:

            # If source had an image, generate prediction card instead
            if event.message.photo:

                match = "Match Prediction"
                prediction = cleaned[:40]

                card = create_prediction_card(match, prediction)

                await client.send_file(target, card)

            else:

                await client.send_message(target, formatted)

        prob = extract_probabilities(text)

        if prob:

            t1,t2,p1,p2 = prob

            chart = create_chart(t1,t2,p1,p2)

            for target in TARGET_CHATS:
                await client.send_file(target, chart)

        save_analytics(cleaned)

    except Exception as e:
        print("Error:", e)

# =============================
# STABLE RUNNER
# =============================

async def run_bot():

    while True:

        try:

            while not internet_ok():
                print("Waiting for internet...")
                await asyncio.sleep(30)

            print("🚀 Orange Bot Running")

            await client.start()
            await client.run_until_disconnected()

        except Exception as e:

            print("Restarting bot:", e)

            await asyncio.sleep(10)

# =============================

if __name__ == "__main__":
    asyncio.run(run_bot())
