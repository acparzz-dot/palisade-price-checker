import requests
import pdfplumber
import re
import io
import telegram
import os

PDF_URL = "https://www.hyundai.com/content/dam/hyundai/kz/ru/files/prices/palisade-2025_ru.pdf"
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = telegram.Bot(token=TOKEN)

def fetch_prices():
    r = requests.get(PDF_URL)
    r.raise_for_status()
    with pdfplumber.open(io.BytesIO(r.content)) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    # Найдём все блоки, которые начинаются с заголовка
    pattern = re.compile(
        r"(Акционная\s+цена\s+\(Автомобили\s+2025\s+г\.в\.\)\s+Luxe\s+Calligraphy\s+"
        r"С бензиновым[^\n]+?₸[^\n]+₸)",
        re.IGNORECASE
    )

    matches = pattern.findall(text)
    if not matches:
        return None

    results = []
    for match in matches:
        # Внутри каждого блока найдём конфигурации с ценами
        rows = re.findall(r"(С бензиновым[^\n]+?)\s+([\d\s]+₸)\s+([\d\s]+₸)", match)
        results.extend(rows)

    return results if results else None

def main():
    prices = fetch_prices()
    if prices:
        message_lines = ["Акционные цены Palisade 2025:"]
        for config, old_price, new_price in prices:
            config_clean = " ".join(config.split())
            old_price_clean = old_price.strip()
            new_price_clean = new_price.strip()
            message_lines.append(f"{config_clean}: {old_price_clean} → {new_price_clean}")
        bot.send_message(CHAT_ID, "\n".join(message_lines))
    else:
        bot.send_message(CHAT_ID, "⚠ Акционные цены не найдены в прайс-листе.")

if __name__ == "__main__":
    main()
