import requests
import pdfplumber
import re
import io
import telegram
import os

PDF_URL = "https://www.hyundai.com/content/dam/hyundai/kz/ru/files/prices/palisade-2025_ru.pdf"
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LAST_PRICE_FILE = "last_price.txt"

bot = telegram.Bot(token=TOKEN)

def fetch_price():
    r = requests.get(PDF_URL)
    r.raise_for_status()
    with pdfplumber.open(io.BytesIO(r.content)) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    match = re.search(r"Акционная цена \(Автомобили 2025 г\.в\.\)\s+([\d\s]+₸)", text)
    return match.group(1).strip() if match else None

def main():
    price = fetch_price()

    old_price = None
    if os.path.exists(LAST_PRICE_FILE):
        with open(LAST_PRICE_FILE, "r", encoding="utf-8") as f:
            old_price = f.read().strip()

    if price:
        if price != old_price:
            bot.send_message(CHAT_ID, f"Новая акционная цена Palisade 2025: {price}")
            with open(LAST_PRICE_FILE, "w", encoding="utf-8") as f:
                f.write(price)
    else:
        if old_price != "NO_PRICE":
            bot.send_message(CHAT_ID, "⚠ Акционная цена на Palisade 2025 больше не указана в прайс-листе.")
            with open(LAST_PRICE_FILE, "w", encoding="utf-8") as f:
                f.write("NO_PRICE")

if __name__ == "__main__":
    main()
