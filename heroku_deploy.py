#!/usr/bin/env python3
"""
Версия бота для деплоя на Heroku
"""

import asyncio
import os
import schedule
import time
from datetime import datetime
import pytz
from telegram import Bot
from telegram.error import TelegramError
from crypto_analyzer import CryptoAnalyzer

class HerokuCryptoBot:
    def __init__(self):
        self.bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
        self.analyzer = CryptoAnalyzer()
        self.chat_id = os.getenv('CHAT_ID')
        self.moscow_tz = pytz.timezone("Europe/Moscow")
    
    async def send_daily_recommendations(self):
        """Отправляет ежедневные рекомендации"""
        try:
            # Получаем текущую дату в московском времени
            moscow_time = datetime.now(self.moscow_tz)
            date_str = moscow_time.strftime("%d.%m.%Y")
            
            # Формируем заголовок сообщения
            message = f"🚀 <b>ЕЖЕДНЕВНЫЕ РЕКОМЕНДАЦИИ ПО КРИПТОВАЛЮТАМ</b>\n"
            message += f"📅 Дата: {date_str}\n"
            message += f"💰 Бюджет на день: $10\n"
            message += f"⏰ Время анализа: {moscow_time.strftime('%H:%M')}\n\n"
            message += f"🔍 <b>ТОП-3 КРИПТОВАЛЮТЫ ДЛЯ ПОКУПКИ:</b>\n\n"
            
            # Получаем рекомендации
            recommendations = self.analyzer.get_top_3_recommendations()
            
            if not recommendations:
                message += "❌ К сожалению, не удалось получить рекомендации. Попробуйте позже."
                await self.send_message(message)
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
            await self.send_message(message)
            
        except Exception as e:
            error_message = f"❌ Ошибка при отправке рекомендаций: {str(e)}"
            await self.send_message(error_message)
    
    async def send_message(self, message: str):
        """Отправляет сообщение в Telegram"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            print(f"Сообщение отправлено: {datetime.now()}")
        except TelegramError as e:
            print(f"Ошибка отправки сообщения: {e}")
    
    async def send_startup_message(self):
        """Отправляет сообщение о запуске"""
        message = "🤖 <b>КРИПТО-СОВЕТНИК ЗАПУЩЕН НА HEROKU!</b>\n\n"
        message += "Бот теперь работает 24/7 и будет отправлять ежедневные рекомендации "
        message += "каждый день в 10:00 по московскому времени.\n\n"
        message += "✅ Бот работает стабильно\n"
        message += "✅ Автоматический перезапуск\n"
        message += "✅ Детальные рекомендации\n"
        message += "✅ Анализ в реальном времени"
        
        await self.send_message(message)
    
    def schedule_daily_notifications(self):
        """Настраивает ежедневные уведомления"""
        schedule.every().day.at("10:00").do(
            lambda: asyncio.run(self.send_daily_recommendations())
        )
        print("Ежедневные уведомления запланированы на 10:00")

async def main():
    """Основная функция"""
    # Проверяем переменные окружения
    if not os.getenv('TELEGRAM_BOT_TOKEN') or not os.getenv('CHAT_ID'):
        print("❌ Ошибка: Не указаны TELEGRAM_BOT_TOKEN или CHAT_ID")
        return
    
    bot = HerokuCryptoBot()
    
    # Отправляем сообщение о запуске
    await bot.send_startup_message()
    
    # Настраиваем ежедневные уведомления
    bot.schedule_daily_notifications()
    
    print("🤖 Бот запущен на Heroku! Ожидание ежедневных уведомлений...")
    print("📅 Уведомления будут отправляться каждый день в 10:00")
    
    # Запускаем планировщик
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)  # Проверяем каждую минуту

if __name__ == "__main__":
    asyncio.run(main())

