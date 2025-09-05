#!/usr/bin/env python3
"""
Демонстрационный скрипт крипто-советника
Показывает, как работает анализ без установки зависимостей
"""

import json
import random
from datetime import datetime

def get_demo_recommendations():
    """
    Возвращает демонстрационные рекомендации
    """
    # Примеры популярных криптовалют с реальными данными
    demo_coins = [
        {
            "name": "Cardano",
            "symbol": "ADA",
            "current_price": 0.4850,
            "price_change_24h": -2.3,
            "market_cap_rank": 8,
            "volume_24h": 245600000,
            "investment_score": 8.5,
            "reasons": ["Очень доступная цена", "Входит в топ-100", "Высокая ликвидность"]
        },
        {
            "name": "Polygon",
            "symbol": "MATIC",
            "current_price": 0.8920,
            "price_change_24h": -5.1,
            "market_cap_rank": 14,
            "volume_24h": 156200000,
            "investment_score": 8.2,
            "reasons": ["Хорошая возможность для покупки", "Высокая ликвидность"]
        },
        {
            "name": "Chainlink",
            "symbol": "LINK",
            "current_price": 15.2300,
            "price_change_24h": 1.2,
            "market_cap_rank": 11,
            "volume_24h": 89400000,
            "investment_score": 7.8,
            "reasons": ["Входит в топ-100", "Сбалансированные показатели"]
        }
    ]
    
    return demo_coins

def format_message():
    """
    Форматирует демонстрационное сообщение
    """
    recommendations = get_demo_recommendations()
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    message = f"🚀 ЕЖЕДНЕВНЫЕ РЕКОМЕНДАЦИИ ПО КРИПТОВАЛЮТАМ\n"
    message += f"📅 Дата: {current_time}\n"
    message += f"💰 Бюджет на день: $10\n"
    message += f"⏰ Время анализа: {datetime.now().strftime('%H:%M')}\n\n"
    message += f"🔍 ТОП-3 КРИПТОВАЛЮТЫ ДЛЯ ПОКУПКИ:\n\n"
    
    for i, coin in enumerate(recommendations, 1):
        message += f"{i}. {coin['name']} ({coin['symbol']})\n"
        message += f"   💰 Цена: ${coin['current_price']:.4f}\n"
        message += f"   📈 Изменение за 24ч: {coin['price_change_24h']:.1f}%\n"
        message += f"   🏆 Ранг: #{coin['market_cap_rank']}\n"
        message += f"   📊 Объем: ${coin['volume_24h']/1000000:.1f}M\n"
        message += f"   ⭐ Оценка: {coin['investment_score']:.1f}/10\n"
        message += f"   🤔 Почему купить: {', '.join(coin['reasons'])}\n\n"
    
    message += "💡 ОБЩИЕ СОВЕТЫ:\n"
    message += "• Не вкладывайте больше, чем можете позволить себе потерять\n"
    message += "• Диверсифицируйте портфель\n"
    message += "• Проводите собственное исследование перед покупкой\n"
    message += "• Рассматривайте это как долгосрочную инвестицию\n\n"
    
    message += "⚠️ ОТКАЗ ОТ ОТВЕТСТВЕННОСТИ:\n"
    message += "Это не финансовый совет. Всегда проводите собственное исследование.\n\n"
    
    message += "🔧 Это демонстрационная версия. Для реальной работы установите зависимости и настройте бота."
    
    return message

def main():
    """
    Основная функция демонстрации
    """
    print("🤖 ДЕМОНСТРАЦИЯ КРИПТО-СОВЕТНИКА\n")
    print("=" * 60)
    print()
    
    # Показываем демонстрационное сообщение
    demo_message = format_message()
    print(demo_message)
    
    print("\n" + "=" * 60)
    print("\n📋 КАК ЗАПУСТИТЬ РЕАЛЬНОГО БОТА:")
    print("1. Установите зависимости: pip3 install -r requirements.txt")
    print("2. Настройте конфигурацию: python3 setup.py")
    print("3. Отредактируйте .env файл (укажите токен и Chat ID)")
    print("4. Протестируйте: python3 test_bot.py")
    print("5. Запустите бота: python3 run.py")
    print("\n📖 Подробная инструкция в README.md")

if __name__ == "__main__":
    main()
