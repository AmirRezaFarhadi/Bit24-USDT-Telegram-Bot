import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS = os.getenv("CHAT_ID", "").split(",")  # چند کانال با , جدا کن
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
    result = f"💰 <b>قیمت لحظه‌ای تتر:</b>\n\n🔹 <b>{tether_price_formatted} تومان</b>"
    return tether_price_formatted, result


def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    keyboard = {
        "inline_keyboard": [
            [{"text": "💰 خرید تتر", "url": TETHER_BUY_LINK}]
        ]
    }
    for chat_id in CHAT_IDS:
        if not chat_id.strip():
            continue
        payload = {
            "chat_id": chat_id.strip(),
            "text": text,
            "parse_mode": "HTML",  # به جای Markdown از HTML استفاده می‌کنیم
            "reply_markup": keyboard
        }
        try:
            r = requests.post(url, json=payload, timeout=10)
            print(f"📢 ارسال به {chat_id}: {r.status_code} {r.text}")
        except Exception as e:
            print(f"❌ خطا در ارسال به {chat_id}:", e)


if __name__ == "__main__":
    price, text = get_tether_price()
    if text and "❌" not in text:
        send_to_telegram(text)
    else:
        print(text)
