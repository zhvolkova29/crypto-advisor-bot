#!/usr/bin/env python3
"""
Модуль для анализа облигаций
"""

import requests
import json
import time
import os
import hashlib
from typing import List, Dict, Any
from datetime import datetime
from config import DAILY_BUDGET

class BondsAnalyzer:
    def __init__(self):
        # Используем открытые источники данных об облигациях
        self.base_url = "https://www.treasury.gov"
        
    def get_top_bonds(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Получает топ облигаций
        Используем список популярных облигаций
        """
        # Популярные облигации (US Treasury, корпоративные)
        # Для примера используем фиксированные данные, так как публичные API ограничены
        bonds_data = [
            {
                'symbol': 'US10Y',
                'name': 'US Treasury 10-Year',
                'current_price': 100.0,  # Номинал облигации
                'yield': 4.5,  # Доходность в процентах
                'price_change_24h': 0.2,
                'maturity': '2034',
                'type': 'Government',
                'rating': 'AAA',
                'volume_24h': 1000000000,
                'market_cap': 10000000000000
            },
            {
                'symbol': 'US5Y',
                'name': 'US Treasury 5-Year',
                'current_price': 100.0,
                'yield': 4.2,
                'price_change_24h': 0.1,
                'maturity': '2029',
                'type': 'Government',
                'rating': 'AAA',
                'volume_24h': 800000000,
                'market_cap': 5000000000000
            },
            {
                'symbol': 'US2Y',
                'name': 'US Treasury 2-Year',
                'current_price': 100.0,
                'yield': 4.0,
                'price_change_24h': 0.05,
                'maturity': '2026',
                'type': 'Government',
                'rating': 'AAA',
                'volume_24h': 600000000,
                'market_cap': 3000000000000
            },
            {
                'symbol': 'CORP-A',
                'name': 'Corporate Bond A-Rated',
                'current_price': 98.5,
                'yield': 5.5,
                'price_change_24h': -0.3,
                'maturity': '2028',
                'type': 'Corporate',
                'rating': 'A',
                'volume_24h': 200000000,
                'market_cap': 1000000000000
            },
            {
                'symbol': 'CORP-BBB',
                'name': 'Corporate Bond BBB-Rated',
                'current_price': 97.0,
                'yield': 6.2,
                'price_change_24h': -0.5,
                'maturity': '2027',
                'type': 'Corporate',
                'rating': 'BBB',
                'volume_24h': 150000000,
                'market_cap': 500000000000
            }
        ]
        
        return bonds_data[:limit]
    
    def filter_suitable_bonds(self, bonds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Фильтрует облигации по критериям"""
        suitable = []
        
        for bond in bonds:
            try:
                price = bond.get('current_price', 0)
                yield_rate = bond.get('yield', 0)
                volume = bond.get('volume_24h', 0)
                
                # Критерии: доступная цена, хорошая доходность, достаточная ликвидность
                if (price <= 100.0 and  # Облигации обычно торгуются около номинала
                    price > 50.0 and  # Не слишком дешево (риск дефолта)
                    yield_rate >= 3.0 and  # Минимальная доходность
                    volume >= 100000000):  # Достаточная ликвидность
                    
                    suitable.append(bond)
            except Exception:
                continue
        
        return suitable
    
    def calculate_investment_score(self, bond: Dict[str, Any]) -> float:
        """Рассчитывает оценку привлекательности"""
        score = 0.0
        
        # Оценка по доходности (чем выше, тем лучше)
        yield_rate = bond.get('yield', 0)
        if yield_rate >= 5.0:
            yield_score = 10
        elif yield_rate >= 4.0:
            yield_score = 8
        elif yield_rate >= 3.0:
            yield_score = 6
        else:
            yield_score = 3
        score += yield_score * 0.4
        
        # Оценка по рейтингу (чем выше, тем безопаснее)
        rating = bond.get('rating', '')
        if rating == 'AAA':
            rating_score = 10
        elif rating in ['AA', 'AA+', 'AA-']:
            rating_score = 9
        elif rating in ['A', 'A+', 'A-']:
            rating_score = 8
        elif rating in ['BBB', 'BBB+', 'BBB-']:
            rating_score = 6
        else:
            rating_score = 4
        score += rating_score * 0.3
        
        # Оценка по ликвидности
        volume = bond.get('volume_24h', 0)
        if volume >= 500000000:
            volume_score = 10
        elif volume >= 200000000:
            volume_score = 8
        elif volume >= 100000000:
            volume_score = 6
        else:
            volume_score = 4
        score += volume_score * 0.2
        
        # Оценка по цене (близко к номиналу - лучше)
        price = bond.get('current_price', 100)
        price_diff = abs(price - 100)
        if price_diff <= 1:
            price_score = 10
        elif price_diff <= 3:
            price_score = 8
        elif price_diff <= 5:
            price_score = 6
        else:
            price_score = 4
        score += price_score * 0.1
        
        return score
    
    def get_top_3_recommendations(self) -> List[Dict[str, Any]]:
        """Получает топ-3 рекомендации по облигациям"""
        print("🚀 Начинаем получение рекомендаций по облигациям...")
        
        bonds = self.get_top_bonds(limit=20)
        print(f"📊 Получено {len(bonds) if bonds else 0} облигаций")
        
        suitable = self.filter_suitable_bonds(bonds)
        print(f"✅ Найдено {len(suitable) if suitable else 0} подходящих облигаций")
        
        if not suitable:
            return []
        
        # Рассчитываем оценки
        for bond in suitable:
            bond['investment_score'] = self.calculate_investment_score(bond)
        
        # Сортируем по оценке
        suitable.sort(key=lambda x: x.get('investment_score', 0), reverse=True)
        
        # Возвращаем топ-3
        result = suitable[:3]
        print(f"🏆 Возвращаем {len(result)} рекомендаций")
        return result

