import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("API_KEY")
TETHER_BUY_LINK = "https://bit24.cash/auth?referral=C9BB7CYX"


def get_tether_price():
    url = "https://rest.bit24.cash/pro/capi/v1/markets?page=1"
    headers = {
        "Accept": "application/json",
        "X-BIT24-APIKEY": API_KEY,
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        return None, f"❌ خطا در دریافت API: {e}"

    if not data.get("success", False):
        return None, f"❌ خطا: {data.get('error', {}).get('message', 'ناشناخته')}"

    prices = data.get("data", {}).get("results", [])
    tether_data = next((c for c in prices if c.get("base_coin_name").lower() == "tether"), None)

    if not tether_data:
        return None, "❌ قیمت تتر پیدا نشد."

    tether_price = tether_data.get("last_order", "نامشخص")
    tether_price_formatted = f"{float(tether_price):,.0f}"
    result = f"💰 **قیمت لحظه‌ای تتر:**\n🔹 **{tether_price_formatted} تومان**"
    return tether_price_formatted, result

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    keyboard = {
        "inline_keyboard": [
            [{"text": "💰 خرید تتر", "url": TETHER_BUY_LINK}]
        ]
    }
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": keyboard
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        print("📢 پاسخ تلگرام:", r.text)
    except Exception as e:
        print("❌ خطا در ارسال پیام:", e)

if __name__ == "__main__":
    price, text = get_tether_price()
    if text and "❌" not in text:
        send_to_telegram(text)
    else:
        print(text)





