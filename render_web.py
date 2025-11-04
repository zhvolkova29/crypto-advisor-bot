#!/usr/bin/env python3
"""
Версия интерактивного бота для Render Web Service
"""

import asyncio
import os
import threading
from datetime import datetime
from flask import Flask, jsonify
from interactive_bot import InvestmentAdvisorBot, main as bot_main

# Создаем Flask приложение для Render
app = Flask(__name__)

# Flask маршруты
@app.route('/')
def home():
    return jsonify({
        "status": "Investment Advisor Bot is running",
        "time": datetime.now().isoformat(),
        "message": "Bot is active and ready for user interactions"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

def _start_background_bot_thread():
    """Запуск фонового потока с event loop (совместимо с gunicorn)."""
    def run_bot():
        try:
            print("🚀 Запуск интерактивного бота...")
            asyncio.run(bot_main())
        except Exception as e:
            print(f"❌ Ошибка запуска бота: {e}")
            import traceback
            traceback.print_exc()

    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    print("✅ Бот запущен в фоновом потоке")


# Gunicorn хук: вызывается при инициализации приложения в воркере
def when_ready(server):
    print("🔄 Gunicorn готов, запускаем бота...")
    _start_background_bot_thread()

# Также запускаем при импорте модуля (для совместимости)
_start_background_bot_thread()


if __name__ == "__main__":
    # Локальный запуск
    _start_background_bot_thread()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
