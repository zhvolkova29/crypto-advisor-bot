#!/usr/bin/env python3
"""
Скрипт настройки для крипто-советника
"""

import os
import sys

def create_env_file():
    """Создает файл .env с базовой конфигурацией"""
    env_content = """# Telegram Bot Token (получите у @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# ID чата для отправки уведомлений (ваш личный ID или ID группы)
CHAT_ID=your_chat_id_here

# API ключ для CoinGecko (опционально, для большего количества запросов)
COINGECKO_API_KEY=your_api_key_here
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Создан файл .env")
    else:
        print("ℹ️  Файл .env уже существует")

def check_dependencies():
    """Проверяет установленные зависимости"""
    required_packages = [
        'python-telegram-bot',
        'requests',
        'python-dotenv',
        'schedule',
        'pytz'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Отсутствуют зависимости: {', '.join(missing_packages)}")
        print("Установите их командой: pip install -r requirements.txt")
        return False
    else:
        print("✅ Все зависимости установлены")
        return True

def main():
    """Основная функция настройки"""
    print("🚀 Настройка крипто-советника\n")
    
    # Создаем .env файл
    create_env_file()
    
    # Проверяем зависимости
    if not check_dependencies():
        sys.exit(1)
    
    print("\n📋 Следующие шаги:")
    print("1. Отредактируйте файл .env и укажите:")
    print("   - TELEGRAM_BOT_TOKEN (получите у @BotFather)")
    print("   - CHAT_ID (ваш ID в Telegram)")
    print("2. Запустите тест: python test_bot.py")
    print("3. Запустите бота: python telegram_bot.py")
    
    print("\n📖 Подробная инструкция в README.md")

if __name__ == "__main__":
    main()
