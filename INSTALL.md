# 📋 Инструкции по установке для macOS

## Предварительные требования

### 1. Установка инструментов разработчика
Если у вас возникает ошибка "No developer tools were found", установите Xcode Command Line Tools:

```bash
xcode-select --install
```

### 2. Установка Python
Убедитесь, что у вас установлен Python 3.8+:

```bash
python3 --version
```

Если Python не установлен, скачайте его с [python.org](https://www.python.org/downloads/)

## Установка бота

### 1. Установка зависимостей
```bash
pip3 install -r requirements.txt
```

### 2. Настройка конфигурации
```bash
python3 setup.py
```

### 3. Редактирование .env файла
Откройте файл `.env` и укажите:
- `TELEGRAM_BOT_TOKEN` - токен вашего бота от @BotFather
- `CHAT_ID` - ваш ID в Telegram

### 4. Тестирование
```bash
python3 test_bot.py
```

### 5. Запуск бота
```bash
python3 run.py
```

## Альтернативная установка через Homebrew

Если у вас установлен Homebrew:

```bash
# Установка Python
brew install python

# Установка зависимостей
pip3 install -r requirements.txt
```

## Получение Telegram Bot Token

1. Откройте Telegram
2. Найдите @BotFather
3. Отправьте команду `/newbot`
4. Следуйте инструкциям
5. Сохраните полученный токен

## Получение Chat ID

1. Напишите боту любое сообщение
2. Откройте в браузере: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Найдите `"chat":{"id":123456789}` - это ваш Chat ID

## Устранение проблем

### Ошибка "command not found: python"
Используйте `python3` вместо `python`

### Ошибка с Xcode
Установите Command Line Tools: `xcode-select --install`

### Ошибка с pip
Обновите pip: `python3 -m pip install --upgrade pip`
