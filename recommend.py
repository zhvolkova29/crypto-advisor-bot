#!/usr/bin/env python3
"""
Команда для получения рекомендаций по криптовалютам
"""

import asyncio
from send_detailed_message import send_detailed_recommendations

async def main():
    """Отправляет рекомендации по запросу"""
    print("📤 Отправка рекомендаций по запросу...")
    await send_detailed_recommendations()
    print("✅ Рекомендации отправлены!")

if __name__ == "__main__":
    asyncio.run(main())

