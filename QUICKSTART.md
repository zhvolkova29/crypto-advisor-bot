# ⚡ Быстрый старт

## 🚀 За 5 минут к работающему боту

### 1. Установка зависимостей
```bash
pip3 install -r requirements.txt
```

### 2. Настройка
```bash
python3 setup.py
```

### 3. Получение Telegram Bot Token
1. Откройте Telegram
2. Найдите @BotFather
3. Отправьте `/newbot`
4. Следуйте инструкциям
5. Скопируйте токен

### 4. Получение Chat ID
1. Напишите боту любое сообщение
2. Откройте: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Найдите `"chat":{"id":123456789}`

### 5. Настройка .env файла
Откройте `.env` и замените:
```env
TELEGRAM_BOT_TOKEN=ваш_токен_здесь
CHAT_ID=ваш_chat_id_здесь
```

### 6. Тестирование
```bash
python3 test_bot.py
```

### 7. Запуск
```bash
python3 run.py
```

## 🎯 Что получите

- ✅ Ежедневные рекомендации в 10:00 по Москве
- ✅ Топ-3 криптовалюты для бюджета $10/день
- ✅ Объяснение причин покупки
- ✅ Анализ цены, объема, капитализации

## 🔧 Если что-то не работает

### macOS ошибки:
```bash
xcode-select --install
```

### Python не найден:
```bash
python3 --version
```

### Зависимости не установились:
```bash
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
```

## 📞 Поддержка

- 📖 Полная документация: `README.md`
- 🔧 Установка на macOS: `INSTALL.md`
- 🧪 Демонстрация: `python3 demo.py`
