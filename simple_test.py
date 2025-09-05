#!/usr/bin/env python3
"""
Простой тест бота без установки зависимостей
"""

import os
import urllib.request
import urllib.parse
import json
from datetime import datetime

def load_env():
    """Загружает переменные из .env файла"""
    env_vars = {}
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
        return env_vars
    except FileNotFoundError:
        print("❌ Файл .env не найден!")
        return None

def send_telegram_message(token, chat_id, message):
    """Отправляет сообщение в Telegram"""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        # Кодируем данные
        data = urllib.parse.urlencode(data).encode('utf-8')
        
        # Отправляем запрос
        req = urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        
        result = json.loads(response.read().decode('utf-8'))
        
        if result.get('ok'):
            print("✅ Сообщение отправлено успешно!")
            return True
        else:
            print(f"❌ Ошибка отправки: {result.get('description', 'Неизвестная ошибка')}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def get_crypto_data():
    """Получает данные о криптовалютах"""
    try:
        # Используем бесплатный API CoinGecko
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1&sparkline=false&price_change_percentage=24h"
        
        req = urllib.request.Request(url)
        response = urllib.request.urlopen(req)
        data = json.loads(response.read().decode('utf-8'))
        
        return data
    except Exception as e:
        print(f"❌ Ошибка получения данных: {e}")
        return []

def analyze_cryptocurrencies(crypto_data):
    """Анализирует криптовалюты и выбирает топ-3"""
    suitable_coins = []
    
    for coin in crypto_data:
        try:
            price = coin.get('current_price', 0)
            market_cap = coin.get('market_cap', 0)
            volume = coin.get('total_volume', 0)
            price_change = coin.get('price_change_percentage_24h', 0)
            
            # Фильтруем по критериям
            if (price <= 5 and  # Цена не больше $5
                market_cap >= 10000000 and  # Капитализация не меньше $10M
                volume >= 1000000 and  # Объем не меньше $1M
                price > 0.01):  # Цена не меньше 1 цента
                
                # Рассчитываем оценку
                score = 0
                if price <= 1:
                    score += 3
                if -20 <= price_change <= 10:
                    score += 3
                if market_cap <= 1000000000:
                    score += 2
                if volume >= 5000000:
                    score += 2
                
                coin_info = {
                    'name': coin.get('name', 'Unknown'),
                    'symbol': coin.get('symbol', '').upper(),
                    'price': price,
                    'price_change': price_change,
                    'market_cap_rank': coin.get('market_cap_rank', 0),
                    'volume': volume,
                    'score': score
                }
                
                suitable_coins.append(coin_info)
                
        except Exception as e:
            continue
    
    # Сортируем по оценке и берем топ-3
    suitable_coins.sort(key=lambda x: x['score'], reverse=True)
    return suitable_coins[:3]

def format_message(recommendations):
    """Форматирует сообщение с рекомендациями"""
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    message = f"🚀 <b>ЕЖЕДНЕВНЫЕ РЕКОМЕНДАЦИИ ПО КРИПТОВАЛЮТАМ</b>\n"
    message += f"📅 Дата: {current_time}\n"
    message += f"💰 Бюджет на день: $10\n"
    message += f"⏰ Время анализа: {datetime.now().strftime('%H:%M')}\n\n"
    message += f"🔍 <b>ТОП-3 КРИПТОВАЛЮТЫ ДЛЯ ПОКУПКИ:</b>\n\n"
    
    if not recommendations:
        message += "❌ К сожалению, не удалось получить рекомендации. Попробуйте позже."
        return message
    
    for i, coin in enumerate(recommendations, 1):
        message += f"<b>{i}. {coin['name']} ({coin['symbol']})</b>\n"
        message += f"💰 Цена: ${coin['price']:.4f}\n"
        message += f"📈 Изменение за 24ч: {coin['price_change']:.1f}%\n"
        message += f"🏆 Ранг: #{coin['market_cap_rank']}\n"
        message += f"📊 Объем: ${coin['volume']/1000000:.1f}M\n"
        message += f"⭐ Оценка: {coin['score']}/10\n\n"
        
        # Добавляем объяснение
        reasons = []
        if coin['price'] <= 1:
            reasons.append("✅ Очень доступная цена")
        if -30 <= coin['price_change'] <= -5:
            reasons.append("✅ Хорошая возможность для покупки")
        if coin['market_cap_rank'] <= 100:
            reasons.append("✅ Входит в топ-100")
        if coin['volume'] >= 5000000:
            reasons.append("✅ Высокая ликвидность")
        
        if reasons:
            message += f"🤔 Почему купить: {', '.join(reasons)}\n"
        else:
            message += "🤔 Почему купить: Сбалансированные показатели\n"
        
        message += "\n"
    
    message += "💡 <b>ОБЩИЕ СОВЕТЫ:</b>\n"
    message += "• Не вкладывайте больше, чем можете позволить себе потерять\n"
    message += "• Диверсифицируйте портфель\n"
    message += "• Проводите собственное исследование перед покупкой\n"
    message += "• Рассматривайте это как долгосрочную инвестицию\n\n"
    
    message += "⚠️ <b>ОТКАЗ ОТ ОТВЕТСТВЕННОСТИ:</b>\n"
    message += "Это не финансовый совет. Всегда проводите собственное исследование."
    
    return message

def main():
    """Основная функция"""
    print("🤖 ПРОСТОЙ ТЕСТ КРИПТО-СОВЕТНИКА\n")
    
    # Загружаем конфигурацию
    env_vars = load_env()
    if not env_vars:
        return
    
    token = env_vars.get('TELEGRAM_BOT_TOKEN')
    chat_id = env_vars.get('CHAT_ID')
    
    if not token or not chat_id:
        print("❌ Не указаны TELEGRAM_BOT_TOKEN или CHAT_ID в .env файле")
        return
    
    print(f"✅ Токен: {token[:20]}...")
    print(f"✅ Chat ID: {chat_id}")
    print()
    
    # Отправляем тестовое сообщение
    print("📱 Отправка тестового сообщения...")
    test_message = "🧪 <b>ТЕСТОВОЕ СООБЩЕНИЕ</b>\n\nКрипто-советник работает корректно!\nЭто тестовое сообщение для проверки подключения."
    
    if send_telegram_message(token, chat_id, test_message):
        print("✅ Тестовое сообщение отправлено!")
    else:
        print("❌ Ошибка отправки тестового сообщения")
        return
    
    print()
    
    # Получаем и анализируем криптовалюты
    print("🔍 Получение данных о криптовалютах...")
    crypto_data = get_crypto_data()
    
    if not crypto_data:
        print("❌ Не удалось получить данные о криптовалютах")
        return
    
    print(f"✅ Получено {len(crypto_data)} криптовалют")
    
    # Анализируем и выбираем топ-3
    print("📊 Анализ и выбор топ-3...")
    recommendations = analyze_cryptocurrencies(crypto_data)
    
    if not recommendations:
        print("❌ Не найдено подходящих криптовалют")
        return
    
    print(f"✅ Выбрано {len(recommendations)} рекомендаций")
    
    # Форматируем и отправляем рекомендации
    print("📤 Отправка рекомендаций...")
    message = format_message(recommendations)
    
    if send_telegram_message(token, chat_id, message):
        print("✅ Рекомендации отправлены!")
    else:
        print("❌ Ошибка отправки рекомендаций")
    
    print("\n🎉 Тестирование завершено!")

if __name__ == "__main__":
    main()


