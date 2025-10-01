import requests
import json
from typing import List, Dict, Any
from config import COINGECKO_API_KEY, MIN_MARKET_CAP, MIN_VOLUME_24H, MAX_PRICE_PER_COIN

class CryptoAnalyzer:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.headers = {
            # CoinGecko иногда требует User-Agent
            'User-Agent': 'CryptoAdvisorBot/1.0 (+https://github.com/)'
        }
        if COINGECKO_API_KEY:
            self.headers['X-CG-API-KEY'] = COINGECKO_API_KEY
    
    def get_top_cryptocurrencies(self, limit: int = 250) -> List[Dict[str, Any]]:
        """
        Получает топ криптовалют с базовой информацией
        """
        try:
            url = f"{self.base_url}/coins/markets"
            all_rows: List[Dict[str, Any]] = []
            # CoinGecko per_page максимум 250. Соберем 2 страницы для надежности (до 500 монет)
            pages = 2 if limit > 250 else 1
            per_page = 250 if limit > 250 else limit
            for page in range(1, pages + 1):
                params = {
                    'vs_currency': 'usd',
                    'order': 'market_cap_desc',
                    'per_page': per_page,
                    'page': page,
                    'sparkline': False,
                    'price_change_percentage': '24h,7d'
                }
                response = requests.get(url, params=params, headers=self.headers, timeout=20)
                if response.status_code != 200:
                    print(f"CoinGecko HTTP {response.status_code}: {response.text[:200]}")
                    continue
                rows = response.json()
                if not isinstance(rows, list):
                    print(f"Неожиданный ответ CoinGecko: {rows}")
                    continue
                all_rows.extend(rows)
            return all_rows
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []
    
    def filter_suitable_cryptocurrencies(self, cryptocurrencies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Фильтрует криптовалюты по критериям для инвестирования
        """
        suitable_coins = []
        
        for coin in cryptocurrencies:
            try:
                # Проверяем базовые критерии
                if (coin.get('market_cap', 0) >= MIN_MARKET_CAP and
                    coin.get('total_volume', 0) >= MIN_VOLUME_24H and
                    coin.get('current_price', 0) <= MAX_PRICE_PER_COIN and
                    coin.get('current_price', 0) > 0.01):  # Минимальная цена 1 цент
                    
                    # Добавляем дополнительную информацию
                    coin_info = {
                        'id': coin.get('id'),
                        'symbol': coin.get('symbol', '').upper(),
                        'name': coin.get('name'),
                        'current_price': coin.get('current_price', 0),
                        'market_cap': coin.get('market_cap', 0),
                        'volume_24h': coin.get('total_volume', 0),
                        'price_change_24h': coin.get('price_change_percentage_24h', 0),
                        # CoinGecko возвращает 7д как price_change_percentage_7d_in_currency
                        'price_change_7d': coin.get('price_change_percentage_7d_in_currency', coin.get('price_change_percentage_7d', 0) or 0),
                        'market_cap_rank': coin.get('market_cap_rank', 0),
                        'image': coin.get('image', '')
                    }
                    
                    suitable_coins.append(coin_info)
            except Exception as e:
                print(f"Ошибка при обработке монеты {coin.get('name', 'Unknown')}: {e}")
                continue
        
        return suitable_coins
    
    def calculate_investment_score(self, coin: Dict[str, Any]) -> float:
        """
        Рассчитывает оценку привлекательности для инвестирования
        """
        score = 0.0
        
        # Оценка по цене (чем дешевле, тем лучше)
        price = coin.get('current_price', 0)
        if price > 0:
            price_score = max(0, 10 - price)  # Максимум 10 баллов за очень дешевые монеты
            score += price_score * 0.3
        
        # Оценка по объему торгов (чем больше объем, тем лучше)
        volume = coin.get('volume_24h', 0)
        if volume > 0:
            volume_score = min(10, volume / 10000000)  # 10 баллов за объем > 100M
            score += volume_score * 0.2
        
        # Оценка по капитализации (умеренная капитализация лучше)
        market_cap = coin.get('market_cap', 0)
        if market_cap > 0:
            if 10000000 <= market_cap <= 1000000000:  # 10M - 1B
                market_cap_score = 10
            elif market_cap < 10000000:
                market_cap_score = 5
            else:
                market_cap_score = 7
            score += market_cap_score * 0.2
        
        # Оценка по изменению цены (небольшой рост лучше)
        price_change_24h = coin.get('price_change_24h', 0)
        if -20 <= price_change_24h <= 10:  # Оптимальный диапазон
            price_change_score = 10
        elif price_change_24h < -20:
            price_change_score = 5  # Возможность для покупки на дне
        else:
            price_change_score = 3  # Слишком большой рост
        score += price_change_score * 0.3
        
        return score
    
    def get_top_3_recommendations(self) -> List[Dict[str, Any]]:
        """
        Возвращает топ-3 рекомендации для покупки
        """
        # Получаем топ криптовалют
        cryptocurrencies = self.get_top_cryptocurrencies(limit=200)
        
        # Фильтруем подходящие
        suitable_coins = self.filter_suitable_cryptocurrencies(cryptocurrencies)
        
        # Рассчитываем оценки и сортируем
        for coin in suitable_coins:
            coin['investment_score'] = self.calculate_investment_score(coin)
        
        # Сортируем по оценке инвестирования (по убыванию)
        suitable_coins.sort(key=lambda x: x.get('investment_score', 0), reverse=True)
        
        # Если после фильтра пусто — попробуем запасной легкий фильтр, чтобы не присылать пустое
        if not suitable_coins:
            fallback: List[Dict[str, Any]] = []
            # Возьмем монеты до $5 с объемом > $5M
            cryptocurrencies = self.get_top_cryptocurrencies(limit=500)
            for coin in cryptocurrencies:
                try:
                    if coin.get('current_price', 0) <= MAX_PRICE_PER_COIN and coin.get('total_volume', 0) >= 5_000_000:
                        fallback.append({
                            'id': coin.get('id'),
                            'symbol': coin.get('symbol', '').upper(),
                            'name': coin.get('name'),
                            'current_price': coin.get('current_price', 0),
                            'market_cap': coin.get('market_cap', 0),
                            'volume_24h': coin.get('total_volume', 0),
                            'price_change_24h': coin.get('price_change_percentage_24h', coin.get('price_change_percentage_24h_in_currency', 0) or 0),
                            'price_change_7d': coin.get('price_change_percentage_7d_in_currency', 0),
                            'market_cap_rank': coin.get('market_cap_rank', 0),
                            'image': coin.get('image', ''),
                            'investment_score': 0.0,
                        })
                except Exception:
                    continue
            fallback.sort(key=lambda x: (x.get('market_cap_rank') or 10_000))
            return fallback[:3]

        # Возвращаем топ-3
        return suitable_coins[:3]
    
    def get_coin_description(self, coin: Dict[str, Any]) -> str:
        """
        Генерирует детальное описание для криптовалюты
        """
        name = coin.get('name', 'Unknown')
        symbol = coin.get('symbol', '')
        price = coin.get('current_price', 0)
        price_change_24h = coin.get('price_change_24h', 0)
        price_change_7d = coin.get('price_change_7d', 0)
        market_cap_rank = coin.get('market_cap_rank', 0)
        volume_24h = coin.get('volume_24h', 0)
        market_cap = coin.get('market_cap', 0)
        
        description = f"🪙 {name} ({symbol})\n"
        description += f"💰 Цена: ${price:.4f}\n"
        description += f"📈 Изменение за 24ч: {price_change_24h:.1f}%\n"
        description += f"📊 Изменение за 7 дней: {price_change_7d:.1f}%\n"
        description += f"🏆 Ранг по капитализации: #{market_cap_rank}\n"
        description += f"📊 Объем торгов: ${volume_24h/1000000:.1f}M\n"
        description += f"💎 Капитализация: ${market_cap/1000000:.1f}M\n\n"
        
        # Детальный анализ причин покупки
        reasons = []
        
        # Анализ цены
        if price <= 0.1:
            reasons.append("✅ Сверхдоступная цена - за $10 можно купить {:.0f} монет".format(10/price))
        elif price <= 0.5:
            reasons.append("✅ Очень доступная цена - за $10 можно купить {:.0f} монет".format(10/price))
        elif price <= 1:
            reasons.append("✅ Доступная цена - за $10 можно купить {:.0f} монет".format(10/price))
        elif price <= 2:
            reasons.append("✅ Умеренная цена - за $10 можно купить {:.0f} монет".format(10/price))
        
        # Анализ изменения цены
        if price_change_24h <= -15:
            reasons.append("✅ Сильная просадка (-{:.1f}%) - отличная возможность для покупки на дне".format(abs(price_change_24h)))
        elif price_change_24h <= -8:
            reasons.append("✅ Значительное падение (-{:.1f}%) - хороший момент для входа".format(abs(price_change_24h)))
        elif price_change_24h <= -3:
            reasons.append("✅ Небольшая коррекция (-{:.1f}%) - подходящее время для покупки".format(abs(price_change_24h)))
        elif price_change_24h >= 15:
            reasons.append("⚠️ Сильный рост (+{:.1f}%) - возможна коррекция, но тренд позитивный".format(price_change_24h))
        elif price_change_24h >= 5:
            reasons.append("✅ Позитивный тренд (+{:.1f}%) - монета набирает силу".format(price_change_24h))
        
        # Анализ недельного тренда
        if price_change_7d <= -20:
            reasons.append("📉 Недельная просадка -{:.1f}% - возможно дно, потенциал отскока".format(abs(price_change_7d)))
        elif price_change_7d >= 20:
            reasons.append("📈 Недельный рост +{:.1f}% - сильный восходящий тренд".format(price_change_7d))
        
        # Анализ ранга и капитализации
        if market_cap_rank <= 50:
            reasons.append("🏆 Топ-50 проект - высокая стабильность и доверие рынка")
        elif market_cap_rank <= 100:
            reasons.append("🥈 Топ-100 проект - хороший баланс стабильности и роста")
        elif market_cap_rank <= 200:
            reasons.append("🥉 Топ-200 проект - перспективный рост с умеренным риском")
        elif market_cap_rank <= 500:
            reasons.append("💎 Топ-500 проект - высокий потенциал роста")
        
        # Анализ ликвидности
        if volume_24h >= 100000000:  # 100M+
            reasons.append("💧 Очень высокая ликвидность - мгновенная покупка/продажа")
        elif volume_24h >= 50000000:  # 50M+
            reasons.append("🌊 Высокая ликвидность - легко торговать")
        elif volume_24h >= 10000000:  # 10M+
            reasons.append("💦 Хорошая ликвидность - стабильные торги")
        elif volume_24h >= 5000000:  # 5M+
            reasons.append("💧 Умеренная ликвидность - торги возможны")
        
        # Анализ капитализации
        if market_cap >= 1000000000:  # 1B+
            reasons.append("💎 Крупная капитализация - низкий риск, стабильный рост")
        elif market_cap >= 100000000:  # 100M+
            reasons.append("💎 Средняя капитализация - хороший потенциал роста")
        elif market_cap >= 10000000:  # 10M+
            reasons.append("💎 Малый проект - высокий риск, но большой потенциал")
        
        # Специальные случаи
        if price_change_24h > 0 and price_change_7d > 0:
            reasons.append("🚀 Двойной позитивный тренд - 24ч и 7д рост")
        elif price_change_24h < 0 and price_change_7d < 0:
            reasons.append("📉 Двойная просадка - возможен отскок от дна")
        
        # Если нет конкретных причин
        if not reasons:
            reasons.append("✅ Сбалансированные показатели - подходит для долгосрочного портфеля")
        
        description += "🤔 Почему стоит купить:\n"
        for reason in reasons:
            description += f"{reason}\n"
        
        # Добавляем риск-факторы
        risk_factors = []
        if price_change_24h <= -20:
            risk_factors.append("⚠️ Высокая волатильность - возможны дальнейшие падения")
        if volume_24h < 1000000:
            risk_factors.append("⚠️ Низкая ликвидность - сложно продать при необходимости")
        if market_cap_rank > 1000:
            risk_factors.append("⚠️ Высокий риск - малый проект")
        
        if risk_factors:
            description += "\n⚠️ Риск-факторы:\n"
            for risk in risk_factors:
                description += f"{risk}\n"
        
        return description
