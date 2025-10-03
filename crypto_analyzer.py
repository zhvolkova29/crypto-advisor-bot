import requests
import json
from typing import List, Dict, Any
import time
import os
import hashlib
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
    
    def _cache_path(self, key: str) -> str:
        digest = hashlib.sha256(key.encode('utf-8')).hexdigest()
        return os.path.join('/tmp', f'coingecko_cache_{digest}.json')

    def _read_cache(self, key: str, ttl_seconds: int = 900) -> List[Dict[str, Any]]:
        try:
            path = self._cache_path(key)
            if not os.path.exists(path):
                return []
            # TTL check
            if time.time() - os.path.getmtime(path) > ttl_seconds:
                return []
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _write_cache(self, key: str, data: List[Dict[str, Any]]) -> None:
        try:
            path = self._cache_path(key)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception:
            pass

    def get_top_cryptocurrencies(self, limit: int = 150) -> List[Dict[str, Any]]:
        """
        Получает топ криптовалют с базовой информацией
        """
        # Пробуем CoinGecko
        cg_data = self._try_coingecko(limit)
        if cg_data:
            return cg_data
        
        # Если CoinGecko не работает, пробуем альтернативный источник
        print("CoinGecko недоступен, используем альтернативный источник...")
        return self._try_alternative_source(limit)
    
    def _try_coingecko(self, limit: int) -> List[Dict[str, Any]]:
        """Пробует получить данные с CoinGecko"""
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': min(250, limit),
                'page': 1,
                'sparkline': False,
                'price_change_percentage': '24h,7d'
            }

            cache_key = f"coins_markets_{params['vs_currency']}_{params['per_page']}_{params['page']}"
            cached = self._read_cache(cache_key)
            if cached:
                return cached

            max_retries = 2  # Уменьшили количество попыток
            backoff = 5
            for attempt in range(max_retries):
                response = requests.get(url, params=params, headers=self.headers, timeout=15)
                if response.status_code == 200:
                    rows = response.json()
                    if isinstance(rows, list) and rows:
                        self._write_cache(cache_key, rows)
                        return rows
                    return []
                
                if response.status_code == 429:
                    print(f"CoinGecko 429. Skipping to alternative source.")
                    return []
                
                print(f"CoinGecko HTTP {response.status_code}: {response.text[:100]}")
                time.sleep(backoff)

            return []
        except Exception as e:
            print(f"CoinGecko error: {e}")
            return []
    
    def _try_alternative_source(self, limit: int) -> List[Dict[str, Any]]:
        """Альтернативный источник данных - CoinCap API"""
        try:
            # Используем CoinCap API (бесплатный, без лимитов)
            url = "https://api.coincap.io/v2/assets"
            params = {
                'limit': min(200, limit),
                'offset': 0
            }
            
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                assets = data.get('data', [])
                
                # Конвертируем формат CoinCap в формат CoinGecko
                converted = []
                for asset in assets:
                    try:
                        converted.append({
                            'id': asset.get('id', '').lower(),
                            'symbol': asset.get('symbol', '').upper(),
                            'name': asset.get('name', ''),
                            'current_price': float(asset.get('priceUsd', 0)),
                            'market_cap': float(asset.get('marketCapUsd', 0)),
                            'total_volume': float(asset.get('volumeUsd24Hr', 0)),
                            'price_change_percentage_24h': float(asset.get('changePercent24Hr', 0)),
                            'price_change_percentage_7d': 0,  # CoinCap не предоставляет 7d
                            'market_cap_rank': int(asset.get('rank', 999999)),
                            'image': f"https://assets.coincap.io/assets/icons/{asset.get('symbol', '').lower()}@2x.png"
                        })
                    except (ValueError, TypeError):
                        continue
                
                print(f"Получено {len(converted)} монет с CoinCap")
                return converted
            else:
                print(f"CoinCap HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"CoinCap error: {e}")
            # Последний резерв - статические данные
            return self._get_fallback_data()
    
    def _get_fallback_data(self) -> List[Dict[str, Any]]:
        """Резервные данные, если все API недоступны"""
        print("Используем резервные данные")
        return [
            {
                'id': 'bitcoin',
                'symbol': 'BTC',
                'name': 'Bitcoin',
                'current_price': 50000.0,
                'market_cap': 1000000000000,
                'total_volume': 25000000000,
                'price_change_percentage_24h': 2.5,
                'price_change_percentage_7d': 5.0,
                'market_cap_rank': 1,
                'image': 'https://assets.coingecko.com/coins/images/1/large/bitcoin.png'
            },
            {
                'id': 'ethereum',
                'symbol': 'ETH',
                'name': 'Ethereum',
                'current_price': 3000.0,
                'market_cap': 360000000000,
                'total_volume': 15000000000,
                'price_change_percentage_24h': 1.8,
                'price_change_percentage_7d': 3.2,
                'market_cap_rank': 2,
                'image': 'https://assets.coingecko.com/coins/images/279/large/ethereum.png'
            },
            {
                'id': 'binancecoin',
                'symbol': 'BNB',
                'name': 'BNB',
                'current_price': 400.0,
                'market_cap': 60000000000,
                'total_volume': 2000000000,
                'price_change_percentage_24h': 0.5,
                'price_change_percentage_7d': 1.2,
                'market_cap_rank': 3,
                'image': 'https://assets.coingecko.com/coins/images/825/large/bnb-icon2_2x.png'
            }
        ]
    
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
        
        # Если подходящих монет мало, ослабляем критерии
        if len(suitable_coins) < 3:
            print(f"Строгие критерии дали {len(suitable_coins)} монет, ослабляем...")
            suitable_coins = []
            
            for coin in cryptocurrencies:
                try:
                    # Ослабленные критерии
                    if (coin.get('current_price', 0) <= 5.0 and  # До $5
                        coin.get('current_price', 0) > 0.001 and  # Минимум 0.1 цент
                        coin.get('total_volume', 0) >= 5000000):  # Объем от $5M
                        
                        coin_info = {
                            'id': coin.get('id'),
                            'symbol': coin.get('symbol', '').upper(),
                            'name': coin.get('name'),
                            'current_price': coin.get('current_price', 0),
                            'market_cap': coin.get('market_cap', 0),
                            'volume_24h': coin.get('total_volume', 0),
                            'price_change_24h': coin.get('price_change_percentage_24h', 0),
                            'price_change_7d': coin.get('price_change_percentage_7d_in_currency', coin.get('price_change_percentage_7d', 0) or 0),
                            'market_cap_rank': coin.get('market_cap_rank', 0),
                            'image': coin.get('image', '')
                        }
                        
                        suitable_coins.append(coin_info)
                except Exception as e:
                    print(f"Ошибка при обработке монеты {coin.get('name', 'Unknown')}: {e}")
                    continue
            
            # Сортируем по рангу (лучшие монеты)
            suitable_coins.sort(key=lambda x: x.get('market_cap_rank', 999999))
        
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
        print("🚀 Начинаем получение рекомендаций...")
        
        # Получаем топ криптовалют
        cryptocurrencies = self.get_top_cryptocurrencies(limit=200)
        
        print(f"📊 Получено {len(cryptocurrencies) if cryptocurrencies else 0} криптовалют")
        
        # Фильтруем подходящие
        suitable_coins = self.filter_suitable_cryptocurrencies(cryptocurrencies)
        
        print(f"✅ Найдено {len(suitable_coins) if suitable_coins else 0} подходящих монет")
        
        # Рассчитываем оценки и сортируем
        for coin in suitable_coins:
            coin['investment_score'] = self.calculate_investment_score(coin)
        
        # Сортируем по оценке инвестирования (по убыванию)
        suitable_coins.sort(key=lambda x: x.get('investment_score', 0), reverse=True)
        
        # Если после фильтра пусто — сформируем fallback из уже полученных данных,
        # чтобы не делать повторный вызов API и не ловить 429.
        if not suitable_coins:
            fallback: List[Dict[str, Any]] = []
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
        result = suitable_coins[:3]
        print(f"🏆 Возвращаем {len(result)} рекомендаций")
        return result
    
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
