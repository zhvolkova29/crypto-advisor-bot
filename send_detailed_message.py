#!/usr/bin/env python3
"""
Скрипт для отправки детального сообщения с рекомендациями
"""

import asyncio
from telegram import Bot
from telegram.error import TelegramError
from crypto_analyzer import CryptoAnalyzer
from config import TELEGRAM_BOT_TOKEN, CHAT_ID, DAILY_BUDGET
from datetime import datetime
import pytz

async def send_detailed_recommendations():
    """
    Отправляет детальные рекомендации в Telegram
    """
    try:
        # Инициализируем бота и анализатор
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        analyzer = CryptoAnalyzer()
        moscow_tz = pytz.timezone("Europe/Moscow")
        
        # Получаем текущую дату в московском времени
        moscow_time = datetime.now(moscow_tz)
        date_str = moscow_time.strftime("%d.%m.%Y")
        
        # Формируем заголовок сообщения
        message = f"🚀 <b>ЕЖЕДНЕВНЫЕ РЕКОМЕНДАЦИИ ПО КРИПТОВАЛЮТАМ</b>\n"
        message += f"📅 Дата: {date_str}\n"
        message += f"💰 Бюджет на день: ${DAILY_BUDGET}\n"
        message += f"⏰ Время анализа: {moscow_time.strftime('%H:%M')}\n\n"
        message += f"🔍 <b>ТОП-3 КРИПТОВАЛЮТЫ ДЛЯ ПОКУПКИ:</b>\n\n"
        
        # Получаем рекомендации
        recommendations = analyzer.get_top_3_recommendations()
        
        if not recommendations:
            message += "❌ К сожалению, не удалось получить рекомендации. Попробуйте позже."
            await bot.send_message(
                chat_id=CHAT_ID,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            return
        
        # Добавляем каждую рекомендацию с детальным анализом
        for i, coin in enumerate(recommendations, 1):
            message += f"<b>{i}. {coin['name']} ({coin['symbol']})</b>\n"
            message += f"💰 Цена: ${coin['current_price']:.4f}\n"
            message += f"📈 Изменение за 24ч: {coin['price_change_24h']:.1f}%\n"
            message += f"🏆 Ранг: #{coin['market_cap_rank']}\n"
            message += f"📊 Объем: ${coin['volume_24h']/1000000:.1f}M\n"
            message += f"💎 Капитализация: ${coin.get('market_cap', 0)/1000000:.1f}M\n\n"
            
            # Детальный анализ причин покупки
            reasons = []
            price = coin['current_price']
            price_change = coin['price_change_24h']
            price_change_7d = coin.get('price_change_7d', 0)
            rank = coin['market_cap_rank']
            volume = coin['volume_24h']
            market_cap = coin.get('market_cap', 0)
            
            # Анализ цены
            if price <= 0.1:
                reasons.append(f"✅ Сверхдоступная цена - за $10 можно купить {int(10/price)} монет")
            elif price <= 0.5:
                reasons.append(f"✅ Очень доступная цена - за $10 можно купить {int(10/price)} монет")
            elif price <= 1:
                reasons.append(f"✅ Доступная цена - за $10 можно купить {int(10/price)} монет")
            elif price <= 2:
                reasons.append(f"✅ Умеренная цена - за $10 можно купить {int(10/price)} монет")
            
            # Анализ изменения цены
            if price_change <= -15:
                reasons.append(f"✅ Сильная просадка (-{abs(price_change):.1f}%) - отличная возможность")
            elif price_change <= -8:
                reasons.append(f"✅ Значительное падение (-{abs(price_change):.1f}%) - хороший момент")
            elif price_change <= -3:
                reasons.append(f"✅ Небольшая коррекция (-{abs(price_change):.1f}%) - подходящее время")
            elif price_change >= 15:
                reasons.append(f"⚠️ Сильный рост (+{price_change:.1f}%) - тренд позитивный")
            elif price_change >= 5:
                reasons.append(f"✅ Позитивный тренд (+{price_change:.1f}%) - монета набирает силу")
            
            # Анализ недельного тренда
            if price_change_7d <= -20:
                reasons.append(f"📉 Недельная просадка -{abs(price_change_7d):.1f}% - возможно дно")
            elif price_change_7d >= 20:
                reasons.append(f"📈 Недельный рост +{price_change_7d:.1f}% - сильный тренд")
            
            # Анализ ранга
            if rank <= 50:
                reasons.append("🏆 Топ-50 проект - высокая стабильность")
            elif rank <= 100:
                reasons.append("🥈 Топ-100 проект - хороший баланс")
            elif rank <= 200:
                reasons.append("🥉 Топ-200 проект - перспективный рост")
            elif rank <= 500:
                reasons.append("💎 Топ-500 проект - высокий потенциал")
            
            # Анализ ликвидности
            if volume >= 100000000:
                reasons.append("💧 Очень высокая ликвидность")
            elif volume >= 50000000:
                reasons.append("🌊 Высокая ликвидность")
            elif volume >= 10000000:
                reasons.append("💦 Хорошая ликвидность")
            elif volume >= 5000000:
                reasons.append("💧 Умеренная ликвидность")
            
            # Анализ капитализации
            if market_cap >= 1000000000:
                reasons.append("💎 Крупная капитализация - низкий риск")
            elif market_cap >= 100000000:
                reasons.append("💎 Средняя капитализация - хороший потенциал")
            elif market_cap >= 10000000:
                reasons.append("💎 Малый проект - высокий риск, но большой потенциал")
            
            # Показываем топ-3 причины
            if reasons:
                message += f"🤔 Почему купить: {', '.join(reasons[:3])}\n"
            else:
                message += "🤔 Почему купить: Сбалансированные показатели\n"
            
            message += "\n"
        
        # Добавляем общие советы
        message += "💡 <b>ОБЩИЕ СОВЕТЫ:</b>\n"
        message += "• Не вкладывайте больше, чем можете позволить себе потерять\n"
        message += "• Диверсифицируйте портфель\n"
        message += "• Проводите собственное исследование перед покупкой\n"
        message += "• Рассматривайте это как долгосрочную инвестицию\n\n"
        
        message += "⚠️ <b>ОТКАЗ ОТ ОТВЕТСТВЕННОСТИ:</b>\n"
        message += "Это не финансовый совет. Всегда проводите собственное исследование."
        
        # Отправляем сообщение
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        
        print("✅ Детальное сообщение с рекомендациями отправлено!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

async def main():
    """
    Основная функция
    """
    print("📤 Отправка детального сообщения с рекомендациями...")
    await send_detailed_recommendations()

if __name__ == "__main__":
    asyncio.run(main())


