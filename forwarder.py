"""
ORANGE TELEGRAM ANALYTICS BOT
Forward • Clean • Watermark • Anti-Duplicate • Stable Runner
"""

import re
import asyncio
import hashlib
from telethon import TelegramClient, events
from PIL import Image, ImageDraw, ImageFont


# ======================================
# CONFIGURATION
# ======================================

API_ID = 38957368
API_HASH = "ebc59f4e107ed07c65f4bf081b8d88fd"

SOURCE_CHATS = [-1001329677889]        # source channel/group
TARGET_CHATS = ["orangeprediction"]    # your channel

BRAND_TAG = "\n\n🔥 Powered by Orange"

# words to remove
REMOVE_WORDS = [
    "YUVRAJ SINGH RAJPUT",
    "@Yuvrajsinh7",
    "Yuvraj Singh Rajput"
]

# promo detection
PROMO_WORDS = [
    "ID LO",
    "ONLINE ID",
    "REFILL",
    "WHATSAPP",
    "CREATE ID",
    "DEPOSIT",
    "WITHDRAWAL"
]

sent_hashes = set()

client = TelegramClient("orange_session", API_ID, API_HASH)


# ======================================
# TEXT CLEANING
# ======================================

def remove_names(text):

    for word in REMOVE_WORDS:
        text = text.replace(word, "")

    return text


def remove_links(text):

    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"www\S+", "", text)

    return text


def promo_filter(text):

    for word in PROMO_WORDS:

        if word.lower() in text.lower():
            return True

    return False


# ======================================
# DUPLICATE PROTECTION
# ======================================

def is_duplicate(text):

    h = hashlib.md5(text.encode()).hexdigest()

    if h in sent_hashes:
        return True

    sent_hashes.add(h)
    return False


# ======================================
# WATERMARK FUNCTION
# ======================================

def add_watermark(image_path):

    img = Image.open(image_path).convert("RGBA")

    width, height = img.size

    layer = Image.new("RGBA", img.size, (0,0,0,0))
    draw = ImageDraw.Draw(layer)

    watermark = "ORANGE ANALYTICS"

    size = int(width / 18)

    try:
        font = ImageFont.truetype("arial.ttf", size)
    except:
        font = ImageFont.load_default()

    text_w, text_h = draw.textsize(watermark, font)

    pos = (width - text_w - 40, height - text_h - 40)

    draw.text(
        pos,
        watermark,
        fill=(255,140,0,180),
        font=font
    )

    final = Image.alpha_composite(img, layer)

    output = "watermarked.png"

    final.convert("RGB").save(output)

    return output


# ======================================
# MESSAGE HANDLER
# ======================================

@client.on(events.NewMessage(chats=SOURCE_CHATS))
async def handler(event):

    # skip videos
    if event.message.video:
        return

    text = event.raw_text or ""

    text = remove_names(text)

    text = remove_links(text)

    # skip promo ads
    if promo_filter(text):
        return

    if text and is_duplicate(text):
        return

    final_text = text + BRAND_TAG

    for target in TARGET_CHATS:

        if event.message.photo:

            path = await event.download_media()

            watermarked = add_watermark(path)

            await client.send_file(
                target,
                watermarked,
                caption=final_text
            )

        else:

            await client.send_message(
                target,
                final_text
            )


# ======================================
# STABLE RUNNER
# ======================================

async def run_bot():

    while True:

        try:

            print("🚀 Orange Bot Running...")

            await client.start()

            await client.run_until_disconnected()

        except Exception as e:

            print("⚠️ Error:", e)

            await asyncio.sleep(10)


# ======================================
# START BOT
# ======================================

if __name__ == "__main__":

    asyncio.run(run_bot())
