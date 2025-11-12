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
bot_initialized = False
init_lock = threading.Lock()

def initialize_bot():
    """Инициализация бота (синхронно, без async)"""
    global bot_application, investment_bot, bot_initialized
    
    if bot_initialized:
        return True
    
    with init_lock:
        if bot_initialized:
            return True
        
        try:
            if not TELEGRAM_BOT_TOKEN:
                logger.error("❌ Ошибка: Не указан TELEGRAM_BOT_TOKEN")
                return False
            
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
            
            bot_initialized = True
            logger.info("✅✅✅ Бот полностью инициализирован и готов к работе через webhook")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации бота: {e}")
            import traceback
            traceback.print_exc()
            bot_initialized = False
            return False

# Инициализируем бота при импорте модуля
logger.info("=" * 60)
logger.info("🚀 НАЧАЛО ИНИЦИАЛИЗАЦИИ БОТА ПРИ СТАРТЕ ПРИЛОЖЕНИЯ")
logger.info("=" * 60)
initialize_bot()

# Flask маршруты
@app.route('/')
def home():
    status = initialize_bot()
    return jsonify({
        "status": "Investment Advisor Bot is running",
        "time": datetime.now().isoformat(),
        "message": "Bot is active and ready for user interactions via webhook",
        "webhook_url": os.environ.get('WEBHOOK_URL', request.url_root + 'webhook'),
        "bot_initialized": bot_initialized
    })

@app.route('/health')
def health():
    status = initialize_bot()
    return jsonify({
        "status": "healthy",
        "bot_initialized": bot_initialized,
        "bot_application_exists": bot_application is not None
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint для получения обновлений от Telegram"""
    if not initialize_bot():
        logger.error("❌ Бот не инициализирован для обработки webhook")
        return jsonify({"status": "error", "message": "Bot not initialized"}), 500
    
    if bot_application is None:
        logger.error("❌ Bot application не создан для обработки webhook")
        return jsonify({"status": "error", "message": "Bot application not created"}), 500
    
    try:
        # Получаем JSON данные
        json_data = request.get_json(force=True)
        logger.info(f"📨 Получено обновление: {json_data.get('update_id', 'unknown')}")
        
        # Создаем Update из JSON
        update = Update.de_json(json_data, bot_application.bot)
        
        # Обрабатываем обновление в новом event loop
        # Используем asyncio.run() для каждого обновления
        async def process_update_async():
            """Обрабатывает обновление асинхронно"""
            try:
                # Инициализируем Application через контекстный менеджер
                async with bot_application:
                    # Обрабатываем обновление
                    await bot_application.process_update(update)
            except Exception as e:
                logger.error(f"❌ Ошибка обработки обновления: {e}")
                import traceback
                traceback.print_exc()
                raise
        
        # Запускаем обработку обновления
        asyncio.run(process_update_async())
        
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"❌ Ошибка обработки webhook: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/set-webhook', methods=['GET', 'POST'])
def set_webhook():
    """Устанавливает webhook для бота"""
    if not initialize_bot():
        logger.error("❌ Бот не инициализирован для установки webhook")
        return jsonify({
            "status": "error",
            "message": "Bot not initialized",
            "bot_initialized": bot_initialized,
            "bot_application_exists": bot_application is not None
        }), 500
    
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
        
        # Устанавливаем webhook асинхронно
        async def set_webhook_async():
            """Устанавливает webhook асинхронно"""
            async with bot_application:
                result = await bot_application.bot.set_webhook(webhook_url)
                return result
        
        result = asyncio.run(set_webhook_async())
        
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
    if not initialize_bot():
        return jsonify({"status": "error", "message": "Bot not initialized"}), 500
    
    try:
        async def delete_webhook_async():
            """Удаляет webhook асинхронно"""
            async with bot_application:
                result = await bot_application.bot.delete_webhook()
                return result
        
        result = asyncio.run(delete_webhook_async())
        
        return jsonify({
            "status": "success",
            "message": "Webhook удален",
            "result": result
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
