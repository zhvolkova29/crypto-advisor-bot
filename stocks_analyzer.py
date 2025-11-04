#!/usr/bin/env python3
"""
Модуль для анализа акций
Аналогично crypto_analyzer.py, но для акций
"""

import requests
import json
import time
import os
import hashlib
from typing import List, Dict, Any
from config import MIN_MARKET_CAP, MIN_VOLUME_24H, MAX_PRICE_PER_COIN, DAILY_BUDGET

class StocksAnalyzer:
    def __init__(self):
        # Используем Alpha Vantage API (бесплатный, до 5 запросов/минуту)
        # Или можно использовать Yahoo Finance API
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        
    def _cache_path(self, key: str) -> str:
        """Путь к кешу"""
        digest = hashlib.sha256(key.encode('utf-8')).hexdigest()
        return os.path.join('/tmp', f'stocks_cache_{digest}.json')
    
    def _read_cache(self, key: str, ttl_seconds: int = 900) -> List[Dict[str, Any]]:
        """Читает кеш"""
        try:
            path = self._cache_path(key)
            if not os.path.exists(path):
                return []
            if time.time() - os.path.getmtime(path) > ttl_seconds:
                return []
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    
    def _write_cache(self, key: str, data: List[Dict[str, Any]]) -> None:
        """Записывает в кеш"""
        try:
            path = self._cache_path(key)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception:
            pass
    
    def get_top_stocks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Получает топ акций
        Используем список популярных акций для анализа
        """
        # Популярные акции для анализа
        popular_stocks = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM',
            'V', 'WMT', 'PG', 'JNJ', 'MA', 'DIS', 'HD', 'BAC', 'NFLX',
            'ADBE', 'PYPL', 'CMCSA', 'NKE', 'XOM', 'VZ', 'CSCO', 'PFE',
            'INTC', 'T', 'MRK', 'ABT', 'COST', 'AVGO', 'TMO', 'ACN', 'QCOM',
            'CVX', 'DHR', 'WFC', 'LIN', 'BMY', 'AMGN', 'HON', 'AMAT', 'AMD',
            'LOW', 'RTX', 'UNH', 'INTU', 'DE', 'UBER', 'SPOT', 'ROKU'
        ][:limit]
        
        stocks_data = []
        
        for symbol in popular_stocks:
            try:
                stock_info = self.get_stock_info(symbol)
                if stock_info:
                    stocks_data.append(stock_info)
                time.sleep(0.2)  # Пауза между запросами
            except Exception as e:
                print(f"Ошибка при получении данных для {symbol}: {e}")
                continue
        
        return stocks_data
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Получает информацию об акции"""
        try:
            # Используем Yahoo Finance API (не требует ключа)
            url = f"{self.base_url}/{symbol}"
            params = {
                'interval': '1d',
                'range': '5d'
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                result = data.get('chart', {}).get('result', [])
                
                if result and len(result) > 0:
                    quote = result[0].get('indicators', {}).get('quote', [{}])[0]
                    meta = result[0].get('meta', {})
                    
                    current_price = quote.get('close', [0])[-1] if quote.get('close') else meta.get('regularMarketPrice', 0)
                    previous_close = quote.get('close', [0])[-2] if len(quote.get('close', [])) > 1 else current_price
                    
                    price_change_24h = ((current_price - previous_close) / previous_close * 100) if previous_close else 0
                    
                    return {
                        'symbol': symbol,
                        'name': meta.get('longName', symbol),
                        'current_price': float(current_price),
                        'price_change_24h': float(price_change_24h),
                        'price_change_7d': 0,  # Будет рассчитано позже
                        'market_cap': meta.get('marketCap', 0),
                        'volume_24h': meta.get('regularMarketVolume', 0),
                        'market_cap_rank': 0,  # Для акций не используется
                        'image': f"https://logo.clearbit.com/{meta.get('exchange', 'NYSE')}.com"
                    }
        except Exception as e:
            print(f"Ошибка получения данных для {symbol}: {e}")
        
        return None
    
    def filter_suitable_stocks(self, stocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Фильтрует акции по критериям"""
        suitable = []
        
        for stock in stocks:
            try:
                price = stock.get('current_price', 0)
                market_cap = stock.get('market_cap', 0)
                volume = stock.get('volume_24h', 0)
                
                # Критерии: цена до $10, достаточная капитализация и объем
                if (price <= MAX_PRICE_PER_COIN and 
                    price > 0.01 and
                    market_cap >= MIN_MARKET_CAP and
                    volume >= MIN_VOLUME_24H):
                    
                    suitable.append(stock)
            except Exception:
                continue
        
        # Если подходящих акций мало, ослабляем критерии
        if len(suitable) < 3:
            suitable = []
            for stock in stocks:
                try:
                    price = stock.get('current_price', 0)
                    volume = stock.get('volume_24h', 0)
                    
                    if (price <= 10.0 and 
                        price > 0.01 and
                        volume >= 5000000):
                        suitable.append(stock)
                except Exception:
                    continue
            
            suitable.sort(key=lambda x: x.get('market_cap', 0), reverse=True)
        
        return suitable
    
    def calculate_investment_score(self, stock: Dict[str, Any]) -> float:
        """Рассчитывает оценку привлекательности"""
        score = 0.0
        
        price = stock.get('current_price', 0)
        if price > 0:
            price_score = max(0, 10 - price)
            score += price_score * 0.3
        
        volume = stock.get('volume_24h', 0)
        if volume > 0:
            volume_score = min(10, volume / 10000000)
            score += volume_score * 0.2
        
        market_cap = stock.get('market_cap', 0)
        if market_cap > 0:
            if 1000000000 <= market_cap <= 100000000000:  # 1B - 100B
                market_cap_score = 10
            else:
                market_cap_score = 7
            score += market_cap_score * 0.2
        
        price_change = stock.get('price_change_24h', 0)
        if -20 <= price_change <= 10:
            price_change_score = 10
        elif price_change < -20:
            price_change_score = 5
        else:
            price_change_score = 3
        score += price_change_score * 0.3
        
        return score
    
    def get_top_3_recommendations(self) -> List[Dict[str, Any]]:
        """Получает топ-3 рекомендации по акциям"""
        print("🚀 Начинаем получение рекомендаций по акциям...")
        
        stocks = self.get_top_stocks(limit=30)
        print(f"📊 Получено {len(stocks) if stocks else 0} акций")
        
        suitable = self.filter_suitable_stocks(stocks)
        print(f"✅ Найдено {len(suitable) if suitable else 0} подходящих акций")
        
        if not suitable:
            return []
        
        # Рассчитываем оценки
        for stock in suitable:
            stock['investment_score'] = self.calculate_investment_score(stock)
        
        # Сортируем по оценке
        suitable.sort(key=lambda x: x.get('investment_score', 0), reverse=True)
        
        # Возвращаем топ-3
        result = suitable[:3]
        print(f"🏆 Возвращаем {len(result)} рекомендаций")
        return result

