#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы крипто-советника
Запускает анализ и отправляет рекомендации сразу
"""

import asyncio
from crypto_analyzer import CryptoAnalyzer
from config import TELEGRAM_BOT_TOKEN, CHAT_ID

async def test_analysis():
    """
    Тестирует анализ криптовалют без отправки в Telegram
    """
    print("🔍 Тестирование анализа криптовалют...")
    
    analyzer = CryptoAnalyzer()
    
    try:
        # Получаем рекомендации
        recommendations = analyzer.get_top_3_recommendations()
        
        if not recommendations:
            print("❌ Не удалось получить рекомендации")
            return
        
        print(f"✅ Получено {len(recommendations)} рекомендаций:\n")
        
        for i, coin in enumerate(recommendations, 1):
            print(f"{i}. {coin['name']} ({coin['symbol']})")
            print(f"   💰 Цена: ${coin['current_price']:.4f}")
            print(f"   📈 Изменение за 24ч: {coin['price_change_24h']:.1f}%")
            print(f"   🏆 Ранг: #{coin['market_cap_rank']}")
            print(f"   📊 Объем: ${coin['volume_24h']/1000000:.1f}M")
            print(f"   ⭐ Оценка: {coin.get('investment_score', 0):.2f}/10")
            print()
            
            # Показываем описание
            description = analyzer.get_coin_description(coin)
            print(description)
            print("-" * 50)
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")

async def test_telegram_send():
    """
    Тестирует отправку сообщения в Telegram
    """
    if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
        print("❌ Не настроены TELEGRAM_BOT_TOKEN или CHAT_ID")
        return
    
    print("📱 Тестирование отправки в Telegram...")
    
    try:
        from telegram import Bot
        from telegram.error import TelegramError
        
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Тестовое сообщение
        test_message = "🧪 <b>ТЕСТОВОЕ СООБЩЕНИЕ</b>\n\n"
        test_message += "Крипто-советник работает корректно!\n"
        test_message += "Это тестовое сообщение для проверки подключения."
        
        await bot.send_message(
            chat_id=CHAT_ID,
            text=test_message,
            parse_mode='HTML'
        )
        
        print("✅ Тестовое сообщение отправлено в Telegram")
        
    except TelegramError as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")

async def main():
    """
    Основная функция тестирования
    """
    print("🚀 Запуск тестирования крипто-советника\n")
    
    # Тест анализа
    await test_analysis()
    
    print("\n" + "="*60 + "\n")
    
    # Тест Telegram
    await test_telegram_send()
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    asyncio.run(main())
