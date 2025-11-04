#!/usr/bin/env python3
"""
Интерактивный бот-советник по инвестициям
Поддерживает акции, облигации и криптовалюты
"""

import asyncio
import os
from datetime import datetime
import pytz
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError
from crypto_analyzer import CryptoAnalyzer
from stocks_analyzer import StocksAnalyzer
from bonds_analyzer import BondsAnalyzer
from config import TELEGRAM_BOT_TOKEN, CHAT_ID, DAILY_BUDGET

class InvestmentAdvisorBot:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.crypto_analyzer = CryptoAnalyzer()
        self.stocks_analyzer = StocksAnalyzer()
        self.bonds_analyzer = BondsAnalyzer()
        self.moscow_tz = pytz.timezone("Europe/Moscow")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_message = (
            "👋 <b>Добро пожаловать в Инвестиционного Советника!</b>\n\n"
            "Я помогу вам выбрать лучшие инвестиционные возможности:\n"
            "• 📈 Акции\n"
            "• 💼 Облигации\n"
            "• 🪙 Криптовалюты\n\n"
            "Нажмите кнопку ниже, чтобы начать!"
        )
        
        keyboard = [
            [InlineKeyboardButton("🚀 Начать инвестировать", callback_data='start_investing')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'start_investing':
            # Показываем выбор типа актива
            await self.show_asset_type_selection(query)
        
        elif query.data == 'stocks':
            await self.show_stocks_recommendations(query)
        
        elif query.data == 'bonds':
            await self.show_bonds_recommendations(query)
        
        elif query.data == 'crypto':
            await self.show_crypto_recommendations(query)
        
        elif query.data == 'back_to_menu':
            await self.show_asset_type_selection(query)
    
    async def show_asset_type_selection(self, query):
        """Показывает меню выбора типа актива"""
        message = (
            "💼 <b>Выберите тип актива для инвестирования:</b>\n\n"
            "💰 Бюджет: $10 в день\n"
            "📅 Дата: " + datetime.now(self.moscow_tz).strftime("%d.%m.%Y") + "\n"
        )
        
        keyboard = [
            [InlineKeyboardButton("📈 Акции", callback_data='stocks')],
            [InlineKeyboardButton("💼 Облигации", callback_data='bonds')],
            [InlineKeyboardButton("🪙 Криптовалюты", callback_data='crypto')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def show_crypto_recommendations(self, query):
        """Показывает рекомендации по криптовалютам"""
        await query.edit_message_text("🔍 Анализирую рынок криптовалют...")
        
        try:
            moscow_time = datetime.now(self.moscow_tz)
            date_str = moscow_time.strftime("%d.%m.%Y")
            
            message = f"🪙 <b>РЕКОМЕНДАЦИИ ПО КРИПТОВАЛЮТАМ</b>\n"
            message += f"📅 Дата: {date_str}\n"
            message += f"💰 Бюджет: ${DAILY_BUDGET}\n\n"
            message += f"🔍 <b>ТОП-3 КРИПТОВАЛЮТЫ:</b>\n\n"
            
            recommendations = self.crypto_analyzer.get_top_3_recommendations()
            
            if not recommendations:
                message += "❌ Не удалось получить рекомендации. Попробуйте позже."
                keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
                return
            
            for i, coin in enumerate(recommendations, 1):
                message += f"<b>{i}. {coin['name']} ({coin['symbol']})</b>\n"
                message += f"💰 Цена: ${coin['current_price']:.4f}\n"
                message += f"📈 Изменение за 24ч: {coin['price_change_24h']:.1f}%\n"
                message += f"🏆 Ранг: #{coin['market_cap_rank']}\n"
                message += f"📊 Объем: ${coin['volume_24h']/1000000:.1f}M\n"
                
                # Причины покупки
                reasons = []
                price = coin['current_price']
                price_change = coin['price_change_24h']
                rank = coin['market_cap_rank']
                volume = coin['volume_24h']
                
                if price <= 0.1:
                    reasons.append(f"✅ Сверхдоступная цена - за $10 можно купить {int(10/price)} монет")
                elif price <= 0.5:
                    reasons.append(f"✅ Очень доступная цена - за $10 можно купить {int(10/price)} монет")
                elif price <= 1:
                    reasons.append(f"✅ Доступная цена - за $10 можно купить {int(10/price)} монет")
                elif price <= 2:
                    reasons.append(f"✅ Умеренная цена - за $10 можно купить {int(10/price)} монет")
                
                if price_change <= -15:
                    reasons.append(f"✅ Сильная просадка (-{abs(price_change):.1f}%) - отличная возможность")
                elif price_change <= -8:
                    reasons.append(f"✅ Значительное падение (-{abs(price_change):.1f}%) - хороший момент")
                elif price_change <= -3:
                    reasons.append(f"✅ Небольшая коррекция (-{abs(price_change):.1f}%) - подходящее время")
                elif price_change >= 5:
                    reasons.append(f"✅ Позитивный тренд (+{price_change:.1f}%)")
                
                if rank <= 100:
                    reasons.append("🥈 Топ-100 проект - хороший баланс")
                elif rank <= 200:
                    reasons.append("🥉 Топ-200 проект - перспективный рост")
                
                if volume >= 50000000:
                    reasons.append("🌊 Высокая ликвидность")
                elif volume >= 10000000:
                    reasons.append("💦 Хорошая ликвидность")
                
                if reasons:
                    message += f"🤔 Почему купить: {', '.join(reasons[:3])}\n"
                message += "\n"
            
            keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
            
        except Exception as e:
            error_message = f"❌ Ошибка при получении рекомендаций: {str(e)}"
            keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(error_message, reply_markup=reply_markup)
    
    async def show_stocks_recommendations(self, query):
        """Показывает рекомендации по акциям"""
        await query.edit_message_text("🔍 Анализирую рынок акций...")
        
        try:
            moscow_time = datetime.now(self.moscow_tz)
            date_str = moscow_time.strftime("%d.%m.%Y")
            
            message = f"📈 <b>РЕКОМЕНДАЦИИ ПО АКЦИЯМ</b>\n"
            message += f"📅 Дата: {date_str}\n"
            message += f"💰 Бюджет: ${DAILY_BUDGET}\n\n"
            message += f"🔍 <b>ТОП-3 АКЦИИ:</b>\n\n"
            
            recommendations = self.stocks_analyzer.get_top_3_recommendations()
            
            if not recommendations:
                message += "❌ Не удалось получить рекомендации. Попробуйте позже."
                keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
                return
            
            for i, stock in enumerate(recommendations, 1):
                message += f"<b>{i}. {stock['name']} ({stock['symbol']})</b>\n"
                message += f"💰 Цена: ${stock['current_price']:.2f}\n"
                message += f"📈 Изменение за 24ч: {stock['price_change_24h']:.1f}%\n"
                message += f"📊 Объем: ${stock['volume_24h']/1000000:.1f}M\n"
                message += f"💎 Капитализация: ${stock['market_cap']/1000000000:.1f}B\n"
                
                # Причины покупки
                reasons = []
                price = stock['current_price']
                price_change = stock['price_change_24h']
                volume = stock['volume_24h']
                market_cap = stock.get('market_cap', 0)
                
                if price <= 1:
                    reasons.append(f"✅ Очень доступная цена - за $10 можно купить {int(10/price)} акций")
                elif price <= 5:
                    reasons.append(f"✅ Доступная цена - за $10 можно купить {int(10/price)} акций")
                elif price <= 10:
                    reasons.append(f"✅ Умеренная цена - за $10 можно купить {int(10/price)} акций")
                
                if price_change <= -10:
                    reasons.append(f"✅ Сильная просадка (-{abs(price_change):.1f}%) - отличная возможность")
                elif price_change <= -5:
                    reasons.append(f"✅ Значительное падение (-{abs(price_change):.1f}%) - хороший момент")
                elif price_change <= -2:
                    reasons.append(f"✅ Небольшая коррекция (-{abs(price_change):.1f}%) - подходящее время")
                
                if market_cap >= 10000000000:  # 10B+
                    reasons.append("🏆 Крупная компания - высокая стабильность")
                elif market_cap >= 1000000000:  # 1B+
                    reasons.append("🥈 Средняя компания - хороший баланс")
                
                if volume >= 100000000:
                    reasons.append("🌊 Высокая ликвидность")
                
                if reasons:
                    message += f"🤔 Почему купить: {', '.join(reasons[:3])}\n"
                message += "\n"
            
            keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
            
        except Exception as e:
            error_message = f"❌ Ошибка при получении рекомендаций: {str(e)}"
            keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(error_message, reply_markup=reply_markup)
    
    async def show_bonds_recommendations(self, query):
        """Показывает рекомендации по облигациям"""
        await query.edit_message_text("🔍 Анализирую рынок облигаций...")
        
        try:
            moscow_time = datetime.now(self.moscow_tz)
            date_str = moscow_time.strftime("%d.%m.%Y")
            
            message = f"💼 <b>РЕКОМЕНДАЦИИ ПО ОБЛИГАЦИЯМ</b>\n"
            message += f"📅 Дата: {date_str}\n"
            message += f"💰 Бюджет: ${DAILY_BUDGET}\n\n"
            message += f"🔍 <b>ТОП-3 ОБЛИГАЦИИ:</b>\n\n"
            
            recommendations = self.bonds_analyzer.get_top_3_recommendations()
            
            if not recommendations:
                message += "❌ Не удалось получить рекомендации. Попробуйте позже."
                keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
                return
            
            for i, bond in enumerate(recommendations, 1):
                message += f"<b>{i}. {bond['name']} ({bond['symbol']})</b>\n"
                message += f"💰 Цена: ${bond['current_price']:.2f}\n"
                message += f"📈 Доходность: {bond['yield']:.2f}%\n"
                message += f"📅 Погашение: {bond['maturity']}\n"
                message += f"🏆 Рейтинг: {bond['rating']}\n"
                message += f"📊 Тип: {bond['type']}\n"
                message += f"📈 Изменение за 24ч: {bond['price_change_24h']:.2f}%\n"
                
                # Причины покупки
                reasons = []
                yield_rate = bond.get('yield', 0)
                rating = bond.get('rating', '')
                bond_type = bond.get('type', '')
                price = bond.get('current_price', 100)
                
                if yield_rate >= 5.0:
                    reasons.append(f"✅ Высокая доходность ({yield_rate:.2f}%)")
                elif yield_rate >= 4.0:
                    reasons.append(f"✅ Хорошая доходность ({yield_rate:.2f}%)")
                
                if rating in ['AAA', 'AA', 'AA+', 'AA-']:
                    reasons.append(f"🏆 Высокий рейтинг ({rating}) - низкий риск")
                elif rating in ['A', 'A+', 'A-']:
                    reasons.append(f"🥈 Хороший рейтинг ({rating})")
                
                if bond_type == 'Government':
                    reasons.append("🛡️ Государственная облигация - максимальная безопасность")
                elif bond_type == 'Corporate':
                    reasons.append("💼 Корпоративная облигация - баланс риска и доходности")
                
                if abs(price - 100) <= 2:
                    reasons.append("✅ Цена близка к номиналу - стабильность")
                
                if reasons:
                    message += f"🤔 Почему купить: {', '.join(reasons[:3])}\n"
                message += "\n"
            
            keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
            
        except Exception as e:
            error_message = f"❌ Ошибка при получении рекомендаций: {str(e)}"
            keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data='back_to_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(error_message, reply_markup=reply_markup)

async def main():
    """Основная функция запуска бота"""
    try:
        if not TELEGRAM_BOT_TOKEN:
            print("❌ Ошибка: Не указан TELEGRAM_BOT_TOKEN в .env файле")
            return
        
        print(f"🔑 Токен получен: {TELEGRAM_BOT_TOKEN[:20]}...")
        
        bot = InvestmentAdvisorBot()
        print("✅ Объект бота создан")
        
        # Создаем приложение
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        print("✅ Приложение создано")
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", bot.start_command))
        application.add_handler(CallbackQueryHandler(bot.button_callback))
        print("✅ Обработчики добавлены")
        
        print("🤖 Интерактивный бот-советник запущен!")
        print("📱 Бот готов к работе. Используйте /start для начала работы.")
        print("🔄 Инициализируем приложение...")
        
        # Инициализируем и запускаем приложение
        await application.initialize()
        await application.start()
        
        print("🔄 Запускаем polling...")
        
        # Запускаем updater
        await application.updater.start_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
        print("✅ Polling запущен, бот готов принимать сообщения!")
        
        # Ожидаем бесконечно
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("⏹️ Остановка бота...")
        finally:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
    except Exception as e:
        print(f"❌ Критическая ошибка при запуске бота: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main())

