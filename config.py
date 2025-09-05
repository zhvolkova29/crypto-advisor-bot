import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройки Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Настройки API
COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY', '')

# Настройки бота
DAILY_BUDGET = 10  # Долларов в день
MAX_MONTHLY_BUDGET = 300  # Долларов в месяц
MAX_PRICE_PER_COIN = 5  # Максимальная цена за монету в долларах

# Время отправки уведомлений (Москва)
NOTIFICATION_TIME = "10:00"
TIMEZONE = "Europe/Moscow"

# Параметры для анализа криптовалют
MIN_MARKET_CAP = 10000000  # Минимальная капитализация в долларах
MIN_VOLUME_24H = 1000000   # Минимальный объем торгов за 24 часа
