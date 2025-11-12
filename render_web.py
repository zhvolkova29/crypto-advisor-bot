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
init_event = threading.Event()

async def initialize_bot_async():
    """Асинхронная инициализация бота"""
    global bot_application, investment_bot, bot_initialized
    
    try:
        if not TELEGRAM_BOT_TOKEN:
            logger.error("❌ Ошибка: Не указан TELEGRAM_BOT_TOKEN")
            init_event.set()
            return
        
        logger.info("🚀 Начало инициализации интерактивного бота...")
        logger.info(f"🔑 Токен получен: {TELEGRAM_BOT_TOKEN[:20]}...")
        
        logger.info("📦 Создание InvestmentAdvisorBot...")
        investment_bot = InvestmentAdvisorBot()
        logger.info("✅ InvestmentAdvisorBot создан")
        
        logger.info("📦 Создание Application...")
        bot_application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        logger.info("✅ Application создан")
        
        logger.info("📦 Добавление обработчиков...")
        bot_application.add_handler(CommandHandler("start", investment_bot.start_command))
        bot_application.add_handler(CallbackQueryHandler(investment_bot.button_callback))
        logger.info("✅ Обработчики добавлены")
        
        logger.info("📦 Инициализация Application...")
        await bot_application.initialize()
        logger.info("✅ Application инициализирован")
        
        logger.info("📦 Запуск Application...")
        await bot_application.start()
        logger.info("✅ Application запущен")
        
        bot_initialized = True
        logger.info("✅✅✅ Бот полностью инициализирован и готов к работе через webhook")
        init_event.set()  # Сигнализируем, что инициализация завершена
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации бота: {e}")
        import traceback
        traceback.print_exc()
        bot_initialized = False
        init_event.set()  # Все равно сигнализируем, чтобы не зависнуть

def run_bot_loop():
    """Запускает event loop для бота в отдельном потоке"""
    global bot_loop, bot_thread
    
    try:
        logger.info("🔄 Создание нового event loop...")
        bot_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(bot_loop)
        logger.info("✅ Event loop создан")
        
        logger.info("🔄 Запуск задачи инициализации...")
        # Создаем задачу для инициализации
        task = bot_loop.create_task(initialize_bot_async())
        logger.info("✅ Задача инициализации создана")
        
        # Запускаем event loop навсегда
        logger.info("🔄 Запуск event loop навсегда...")
        bot_loop.run_forever()
    except Exception as e:
        logger.error(f"❌ Ошибка в event loop: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if bot_loop and not bot_loop.is_closed():
            logger.info("🔄 Закрытие event loop...")
            bot_loop.close()

def start_bot_thread():
    """Запускает поток для бота"""
    global bot_thread
    
    with init_lock:
        if bot_thread is None or not bot_thread.is_alive():
            logger.info("🚀 Запуск потока для бота...")
            init_event.clear()  # Сбрасываем событие
            bot_thread = threading.Thread(target=run_bot_loop, daemon=True)
            bot_thread.start()
            logger.info("✅ Поток для бота запущен")

def ensure_bot_initialized():
    """Убеждаемся, что бот инициализирован"""
    global bot_initialized
    
    if bot_initialized and bot_application is not None:
        return True
    
    # Запускаем поток, если он еще не запущен
    start_bot_thread()
    
    # Ждем инициализации
    if not bot_initialized:
        logger.info("⏳ Ожидание инициализации бота...")
        if init_event.wait(timeout=30):  # Ждем до 30 секунд
            if bot_initialized:
                logger.info("✅✅✅ Бот успешно инициализирован")
                return True
            else:
                logger.error("❌ Инициализация бота завершилась с ошибкой")
                return False
        else:
            logger.error("❌ Таймаут ожидания инициализации бота (30 секунд)")
            logger.error(f"   bot_initialized={bot_initialized}")
            logger.error(f"   bot_application={bot_application is not None}")
            logger.error(f"   bot_loop={bot_loop is not None}")
            return False
    
    return bot_initialized and bot_application is not None

# Инициализируем бота сразу при импорте модуля
logger.info("=" * 60)
logger.info("🚀 НАЧАЛО ИНИЦИАЛИЗАЦИИ БОТА ПРИ СТАРТЕ ПРИЛОЖЕНИЯ")
logger.info("=" * 60)

# Запускаем поток для бота
start_bot_thread()

# Ждем инициализации в фоне (не блокируем Flask)
def wait_for_initialization():
    """Ждет инициализации бота в фоне"""
    time.sleep(1)  # Даем потоку время на запуск
    ensure_bot_initialized()

threading.Thread(target=wait_for_initialization, daemon=True).start()

# Flask маршруты
@app.route('/')
def home():
    status = ensure_bot_initialized()
    return jsonify({
        "status": "Investment Advisor Bot is running",
        "time": datetime.now().isoformat(),
        "message": "Bot is active and ready for user interactions via webhook",
        "webhook_url": os.environ.get('WEBHOOK_URL', request.url_root + 'webhook'),
        "bot_initialized": bot_initialized,
        "initialization_status": status
    })

@app.route('/health')
def health():
    status = ensure_bot_initialized()
    return jsonify({
        "status": "healthy",
        "bot_initialized": bot_initialized,
        "bot_application_exists": bot_application is not None,
        "bot_loop_exists": bot_loop is not None and not bot_loop.is_closed() if bot_loop else False,
        "initialization_status": status
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint для получения обновлений от Telegram"""
    if not ensure_bot_initialized():
        logger.error("❌ Бот не инициализирован для обработки webhook")
        return jsonify({"status": "error", "message": "Bot not initialized"}), 500
    
    if bot_loop is None or bot_loop.is_closed():
        logger.error("❌ Event loop не запущен для обработки webhook")
        return jsonify({"status": "error", "message": "Event loop not running"}), 500
    
    if bot_application is None:
        logger.error("❌ Bot application не создан для обработки webhook")
        return jsonify({"status": "error", "message": "Bot application not created"}), 500
    
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
        logger.error("❌ Бот не инициализирован для установки webhook")
        return jsonify({
            "status": "error",
            "message": "Bot not initialized",
            "bot_initialized": bot_initialized,
            "bot_application_exists": bot_application is not None,
            "bot_loop_exists": bot_loop is not None and not bot_loop.is_closed() if bot_loop else False
        }), 500
    
    if bot_loop is None or bot_loop.is_closed():
        logger.error("❌ Event loop не запущен для установки webhook")
        return jsonify({"status": "error", "message": "Event loop not running"}), 500
    
    if bot_application is None:
        logger.error("❌ Bot application не создан для установки webhook")
        return jsonify({"status": "error", "message": "Bot application not created"}), 500
    
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
        
        logger.info(f"✅ Webhook установлен: {result}")
        
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
