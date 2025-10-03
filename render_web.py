#!/usr/bin/env python3
"""
Версия бота для Render Web Service
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
from flask import Flask, jsonify

# Создаем Flask приложение для Render
app = Flask(__name__)

class RenderCryptoBot:
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
                rank = coin['market_cap_rank']
                volume = coin['volume_24h']
                
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
        message = "🤖 <b>КРИПТО-СОВЕТНИК ЗАПУЩЕН НА RENDER!</b>\n\n"
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

# Создаем экземпляр бота
crypto_bot = RenderCryptoBot()

# Flask маршруты
@app.route('/')
def home():
    return jsonify({
        "status": "Crypto Advisor Bot is running",
        "time": datetime.now().isoformat(),
        "message": "Bot is active and waiting for 10:00 Moscow time"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/send-recommendations')
def send_recommendations():
    """Отправляет рекомендации по запросу"""
    try:
        # Запускаем в отдельном потоке, чтобы избежать проблем с event loop
        def send_async():
            try:
                asyncio.run(crypto_bot.send_daily_recommendations())
            except Exception as e:
                print(f"Ошибка в send_async: {e}")
        
        thread = threading.Thread(target=send_async)
        thread.daemon = True
        thread.start()
        
        return jsonify({"status": "success", "message": "Recommendations sent"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/test-crypto')
def test_crypto():
    """Тестирование получения криптовалют"""
    try:
        from crypto_analyzer import CryptoAnalyzer
        analyzer = CryptoAnalyzer()
        
        # Тестируем получение данных
        print("🧪 Тестируем получение криптовалют...")
        coins = analyzer.get_top_cryptocurrencies(50)
        print(f"Получено монет: {len(coins) if coins else 0}")
        
        if coins:
            suitable = analyzer.filter_suitable_cryptocurrencies(coins)
            print(f"Подходящих монет: {len(suitable) if suitable else 0}")
            
            if suitable:
                top_3 = analyzer.get_top_3_recommendations()
                print(f"Топ-3 рекомендаций: {len(top_3) if top_3 else 0}")
                
                return jsonify({
                    "message": "Crypto test completed",
                    "coins_found": len(coins) if coins else 0,
                    "suitable_found": len(suitable) if suitable else 0,
                    "recommendations": len(top_3) if top_3 else 0,
                    "status": "success"
                })
            else:
                return jsonify({
                    "message": "No suitable coins found",
                    "coins_found": len(coins) if coins else 0,
                    "status": "warning"
                })
        else:
            return jsonify({
                "message": "No coins retrieved",
                "status": "error"
            })
            
    except Exception as e:
        print(f"❌ Ошибка в тесте: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"message": f"Test error: {str(e)}", "status": "error"})

# Запускаем бота в фоне
async def start_bot():
    """Запускает бота"""
    # Отправляем сообщение о запуске
    await crypto_bot.send_startup_message()
    
    # Настраиваем ежедневные уведомления
    crypto_bot.schedule_daily_notifications()
    
    print("🤖 Бот запущен на Render! Ожидание ежедневных уведомлений...")
    print("📅 Уведомления будут отправляться каждый день в 10:00")
    
    # Запускаем планировщик в фоне
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)  # Проверяем каждую минуту

# Запускаем бота при старте приложения
def _start_background_bot_thread():
    """Запуск фонового потока с event loop (совместимо с gunicorn)."""
    import threading

    def run_bot():
        asyncio.run(start_bot())

    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()


# Gunicorn хук: вызывается при инициализации приложения в воркере
def when_ready(server):
    _start_background_bot_thread()


if __name__ == "__main__":
    # Локальный запуск
    _start_background_bot_thread()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
