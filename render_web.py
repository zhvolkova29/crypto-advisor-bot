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

# Флаг для отслеживания запуска бота
bot_started = False
bot_thread = None

def start_bot():
    """Запуск бота в отдельном потоке"""
    global bot_started, bot_thread
    
    if bot_started:
        return
    
    def run_bot():
        try:
            print("🚀 Запуск интерактивного бота...")
            asyncio.run(bot_main())
        except Exception as e:
            print(f"❌ Ошибка запуска бота: {e}")
            import traceback
            traceback.print_exc()
            # Пытаемся перезапустить через 5 секунд
            threading.Timer(5.0, run_bot).start()

    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    bot_started = True
    print("✅ Бот запущен в фоновом потоке")

# Flask маршруты
@app.route('/')
def home():
    # Запускаем бота при первом запросе
    if not bot_started:
        start_bot()
    
    return jsonify({
        "status": "Investment Advisor Bot is running",
        "time": datetime.now().isoformat(),
        "message": "Bot is active and ready for user interactions",
        "bot_started": bot_started
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "bot_started": bot_started})

# Gunicorn хук
def when_ready(server):
    print("🔄 Gunicorn готов, запускаем бота...")
    start_bot()

# Запускаем бота при импорте модуля
start_bot()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
