#!/usr/bin/env python3
"""
Версия интерактивного бота для Render Web Service с Webhook
"""

import asyncio
import os
import logging
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from interactive_bot import InvestmentAdvisorBot
from config import TELEGRAM_BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Создаем Flask приложение для Render
app = Flask(__name__)

# Глобальные переменные
bot_application = None
investment_bot = None
bot_loop = None
bot_thread = None
bot_initialized = False
init_lock = threading.Lock()

def run_bot_loop():
    """Запускает event loop для бота в отдельном потоке"""
    global bot_loop, bot_application, investment_bot, bot_initialized
    
    bot_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(bot_loop)
    
    try:
        if not TELEGRAM_BOT_TOKEN:
            logger.error("❌ Ошибка: Не указан TELEGRAM_BOT_TOKEN")
            return
        
        logger.info("🚀 Инициализация интерактивного бота...")
        
        investment_bot = InvestmentAdvisorBot()
        bot_application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        bot_application.add_handler(CommandHandler("start", investment_bot.start_command))
        bot_application.add_handler(CallbackQueryHandler(investment_bot.button_callback))
        
        # Инициализируем приложение (но не запускаем polling)
        bot_loop.run_until_complete(bot_application.initialize())
        bot_loop.run_until_complete(bot_application.start())
        
        bot_initialized = True
        logger.info("✅ Бот инициализирован и готов к работе через webhook")
        
        # Запускаем event loop (но не polling)
        bot_loop.run_forever()
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации бота: {e}")
        import traceback
        traceback.print_exc()
        bot_initialized = False
    finally:
        if bot_loop and not bot_loop.is_closed():
            bot_loop.close()

def ensure_bot_initialized():
    """Убеждаемся, что бот инициализирован"""
    global bot_thread, bot_initialized
    
    with init_lock:
        if bot_thread is None or not bot_thread.is_alive():
            if bot_thread is None:
                logger.info("🚀 Запуск потока для бота...")
                bot_thread = threading.Thread(target=run_bot_loop, daemon=True)
                bot_thread.start()
                # Ждем инициализации
                for _ in range(20):  # Ждем до 10 секунд
                    if bot_initialized:
                        break
                    time.sleep(0.5)
                if not bot_initialized:
                    logger.warning("⚠️ Бот еще не инициализирован после ожидания")
    
    return bot_initialized and bot_application is not None

# Flask маршруты
@app.route('/')
def home():
    ensure_bot_initialized()  # Инициализируем при первом запросе
    return jsonify({
        "status": "Investment Advisor Bot is running",
        "time": datetime.now().isoformat(),
        "message": "Bot is active and ready for user interactions via webhook",
        "webhook_url": os.environ.get('WEBHOOK_URL', request.url_root + 'webhook'),
        "bot_initialized": bot_initialized
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "bot_initialized": bot_initialized
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint для получения обновлений от Telegram"""
    if not ensure_bot_initialized():
        logger.error("❌ Бот не инициализирован")
        return jsonify({"status": "error", "message": "Bot not initialized"}), 500
    
    if bot_loop is None or bot_loop.is_closed():
        logger.error("❌ Event loop не запущен")
        return jsonify({"status": "error", "message": "Event loop not running"}), 500
    
    try:
        # Получаем JSON данные
        json_data = request.get_json(force=True)
        logger.info(f"📨 Получено обновление: {json_data.get('update_id', 'unknown')}")
        
        # Создаем Update из JSON
        update = Update.de_json(json_data, bot_application.bot)
        
        # Обрабатываем обновление асинхронно в event loop бота
        future = asyncio.run_coroutine_threadsafe(
            bot_application.process_update(update),
            bot_loop
        )
        # Не ждем результат, чтобы быстро ответить Telegram
        # Ошибки будут логироваться в обработчиках
        
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"❌ Ошибка обработки webhook: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/set-webhook', methods=['GET', 'POST'])
def set_webhook():
    """Устанавливает webhook для бота"""
    if not ensure_bot_initialized():
        return jsonify({"status": "error", "message": "Bot not initialized"}), 500
    
    if bot_loop is None or bot_loop.is_closed():
        return jsonify({"status": "error", "message": "Event loop not running"}), 500
    
    try:
        # Получаем URL для webhook
        webhook_url = os.environ.get('WEBHOOK_URL')
        if not webhook_url:
            # Если не указан в переменных окружения, формируем из request
            scheme = request.headers.get('X-Forwarded-Proto', 'https')
            host = request.headers.get('Host', request.host)
            webhook_url = f"{scheme}://{host}/webhook"
        
        logger.info(f"🔗 Установка webhook: {webhook_url}")
        
        # Устанавливаем webhook асинхронно в event loop бота
        future = asyncio.run_coroutine_threadsafe(
            bot_application.bot.set_webhook(webhook_url),
            bot_loop
        )
        result = future.result(timeout=10)
        
        return jsonify({
            "status": "success",
            "message": "Webhook установлен",
            "url": webhook_url,
            "result": result
        })
    except Exception as e:
        logger.error(f"❌ Ошибка установки webhook: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete-webhook', methods=['GET'])
def delete_webhook():
    """Удаляет webhook (для тестирования)"""
    if not ensure_bot_initialized():
        return jsonify({"status": "error", "message": "Bot not initialized"}), 500
    
    if bot_loop is None or bot_loop.is_closed():
        return jsonify({"status": "error", "message": "Event loop not running"}), 500
    
    try:
        future = asyncio.run_coroutine_threadsafe(
            bot_application.bot.delete_webhook(),
            bot_loop
        )
        result = future.result(timeout=10)
        
        return jsonify({
            "status": "success",
            "message": "Webhook удален",
            "result": result
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Инициализируем бота при локальном запуске
    ensure_bot_initialized()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
