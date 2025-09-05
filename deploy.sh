#!/bin/bash

echo "🚀 Деплой крипто-советника на Heroku"
echo "=================================="

# Проверяем, установлен ли Heroku CLI
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI не установлен"
    echo "Установите: brew tap heroku/brew && brew install heroku"
    exit 1
fi

# Проверяем, авторизован ли пользователь
if ! heroku auth:whoami &> /dev/null; then
    echo "❌ Не авторизован в Heroku"
    echo "Выполните: heroku login"
    exit 1
fi

# Запрашиваем имя приложения
echo "Введите имя для приложения Heroku (или нажмите Enter для автогенерации):"
read app_name

if [ -z "$app_name" ]; then
    echo "Создание приложения с автоматическим именем..."
    heroku create
else
    echo "Создание приложения: $app_name"
    heroku create $app_name
fi

# Получаем имя приложения
APP_NAME=$(heroku apps:info --json | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
echo "✅ Приложение создано: $APP_NAME"

# Настраиваем переменные окружения
echo "Настройка переменных окружения..."

# Проверяем .env файл
if [ -f ".env" ]; then
    echo "📁 Найден файл .env"
    
    # Читаем токен из .env
    TOKEN=$(grep TELEGRAM_BOT_TOKEN .env | cut -d'=' -f2)
    CHAT_ID=$(grep CHAT_ID .env | cut -d'=' -f2)
    
    if [ ! -z "$TOKEN" ] && [ "$TOKEN" != "your_bot_token_here" ]; then
        echo "✅ Найден токен в .env файле"
        heroku config:set TELEGRAM_BOT_TOKEN="$TOKEN" -a $APP_NAME
    else
        echo "❌ Токен не найден в .env файле"
        echo "Введите ваш Telegram Bot Token:"
        read TOKEN
        heroku config:set TELEGRAM_BOT_TOKEN="$TOKEN" -a $APP_NAME
    fi
    
    if [ ! -z "$CHAT_ID" ] && [ "$CHAT_ID" != "your_chat_id_here" ]; then
        echo "✅ Найден Chat ID в .env файле"
        heroku config:set CHAT_ID="$CHAT_ID" -a $APP_NAME
    else
        echo "❌ Chat ID не найден в .env файле"
        echo "Введите ваш Chat ID:"
        read CHAT_ID
        heroku config:set CHAT_ID="$CHAT_ID" -a $APP_NAME
    fi
else
    echo "❌ Файл .env не найден"
    echo "Введите ваш Telegram Bot Token:"
    read TOKEN
    heroku config:set TELEGRAM_BOT_TOKEN="$TOKEN" -a $APP_NAME
    
    echo "Введите ваш Chat ID:"
    read CHAT_ID
    heroku config:set CHAT_ID="$CHAT_ID" -a $APP_NAME
fi

# Инициализируем Git если нужно
if [ ! -d ".git" ]; then
    echo "📁 Инициализация Git репозитория..."
    git init
    git add .
    git commit -m "Initial commit"
fi

# Добавляем Heroku как remote
echo "🔗 Добавление Heroku remote..."
heroku git:remote -a $APP_NAME

# Деплоим код
echo "📤 Деплой кода на Heroku..."
git push heroku main

# Запускаем worker процесс
echo "🤖 Запуск бота..."
heroku ps:scale worker=1 -a $APP_NAME

# Проверяем статус
echo "📊 Проверка статуса..."
heroku ps -a $APP_NAME

echo ""
echo "🎉 Деплой завершен!"
echo "📱 Проверьте Telegram - бот должен отправить сообщение о запуске"
echo ""
echo "🔧 Полезные команды:"
echo "  Логи: heroku logs --tail -a $APP_NAME"
echo "  Статус: heroku ps -a $APP_NAME"
echo "  Остановить: heroku ps:scale worker=0 -a $APP_NAME"
echo "  Запустить: heroku ps:scale worker=1 -a $APP_NAME"
echo "  Тест: heroku run python3 recommend.py -a $APP_NAME"
echo ""
echo "🌐 Ваше приложение: https://$APP_NAME.herokuapp.com"

