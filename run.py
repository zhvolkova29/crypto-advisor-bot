#!/usr/bin/env python3
"""
Простой скрипт для запуска крипто-советника
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def check_config():
    """Проверяет конфигурацию"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    
    if not token or token == 'your_bot_token_here':
        print("❌ Ошибка: Не указан TELEGRAM_BOT_TOKEN в .env файле")
        print("Получите токен у @BotFather в Telegram")
        return False
    
    if not chat_id or chat_id == 'your_chat_id_here':
        print("❌ Ошибка: Не указан CHAT_ID в .env файле")
        print("Узнайте свой Chat ID: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates")
        return False
    
    return True

async def main():
    """Основная функция"""
    print("🤖 Запуск крипто-советника...\n")
    
    # Проверяем конфигурацию
    if not check_config():
        print("\n📋 Для настройки запустите: python3 setup.py")
        sys.exit(1)
    
    try:
        # Импортируем и запускаем бота с детальными рекомендациями
        from send_detailed_message import send_detailed_recommendations
        from telegram_bot import CryptoAdvisorBot
        
        # Создаем экземпляр бота
        bot = CryptoAdvisorBot()
        
        # Отправляем тестовое сообщение
        print("📱 Отправка тестового сообщения...")
        await bot.send_test_message()
        
        # Отправляем детальные рекомендации
        print("📤 Отправка детальных рекомендаций...")
        await send_detailed_recommendations()
        
        # Настраиваем ежедневные уведомления
        bot.schedule_daily_notifications()
        
        print("🤖 Бот запущен! Ожидание ежедневных уведомлений...")
        print("📅 Уведомления будут отправляться каждый день в 10:00")
        print("💡 Для получения рекомендаций сейчас запустите: python3 send_detailed_message.py")
        
        # Запускаем планировщик
        import schedule
        import time
        
        while True:
            schedule.run_pending()
            await asyncio.sleep(60)  # Проверяем каждую минуту
            
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска: {e}")
        print("Попробуйте запустить тест: python3 test_bot.py")

if __name__ == "__main__":
    asyncio.run(main())
