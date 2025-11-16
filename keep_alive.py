"""
Keep-alive сервер для Replit
Предотвращает "засыпание" бота на бесплатном плане Replit
"""
from flask import Flask
from threading import Thread
import time

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    """Запускает Flask сервер в отдельном потоке"""
    t = Thread(target=run)
    t.daemon = True
    t.start()

