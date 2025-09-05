# 🚀 Деплой через GitHub + Heroku

## 📋 Пошаговая инструкция

### 1. Создайте репозиторий на GitHub

1. Перейдите на https://github.com/
2. Нажмите "New repository"
3. Название: `crypto-advisor-bot`
4. Сделайте репозиторий **публичным** (важно для бесплатного Heroku)
5. НЕ добавляйте README, .gitignore или лицензию (у нас уже есть)
6. Нажмите "Create repository"

### 2. Загрузите код на GitHub

Выполните эти команды в терминале:

```bash
# Добавьте GitHub как remote
git remote add origin https://github.com/ВАШ_USERNAME/crypto-advisor-bot.git

# Загрузите код
git branch -M main
git push -u origin main
```

**Замените `ВАШ_USERNAME` на ваш GitHub username!**

### 3. Создайте приложение на Heroku

1. Перейдите на https://dashboard.heroku.com/
2. Нажмите "New" → "Create new app"
3. Имя: `my-crypto-advisor-bot` (или любое другое)
4. Регион: US
5. Нажмите "Create app"

### 4. Подключите GitHub к Heroku

1. В вашем приложении Heroku перейдите в "Deploy"
2. В разделе "Deployment method" выберите "GitHub"
3. Нажмите "Connect to GitHub"
4. Авторизуйтесь в GitHub
5. Найдите ваш репозиторий `crypto-advisor-bot`
6. Нажмите "Connect"

### 5. Настройте переменные окружения

1. В Heroku Dashboard перейдите в "Settings"
2. Нажмите "Reveal Config Vars"
3. Добавьте переменные:

| KEY | VALUE |
|-----|-------|
| `TELEGRAM_BOT_TOKEN` | ваш токен от @BotFather |
| `CHAT_ID` | ваш Chat ID |

### 6. Задеплойте приложение

1. В разделе "Deploy" прокрутите вниз
2. В разделе "Manual deploy" выберите ветку `main`
3. Нажмите "Deploy Branch"
4. Дождитесь завершения деплоя

### 7. Запустите бота

1. Перейдите в "Resources"
2. Найдите "worker" процесс
3. Нажмите на переключатель, чтобы включить его
4. Или нажмите "Edit" и установите количество dynos = 1

### 8. Проверьте работу

1. Перейдите в "More" → "View logs"
2. Вы должны увидеть сообщение о запуске бота
3. Проверьте Telegram - бот должен отправить сообщение

## 🔧 Управление ботом

### Остановить бота:
- В "Resources" выключите worker процесс

### Запустить бота:
- В "Resources" включите worker процесс

### Посмотреть логи:
- "More" → "View logs"

### Отправить тестовое сообщение:
- "More" → "Run console"
- Выполните: `python3 recommend.py`

## ⚠️ Важные моменты

1. **Бесплатный план Heroku:**
   - 550 часов в месяц (23 дня)
   - Бот будет "засыпать" на 7 дней в месяц

2. **Для постоянной работы:**
   - Платный план Heroku ($7/месяц)
   - Или используйте Railway/PythonAnywhere

3. **Мониторинг:**
   - Регулярно проверяйте логи
   - Настройте уведомления о сбоях

## 🎉 Готово!

После успешного деплоя ваш бот будет работать 24/7 и отправлять рекомендации каждый день в 10:00 по Москве!
