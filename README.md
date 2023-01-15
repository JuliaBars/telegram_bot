# Проект Homework Bot

### ![Я](https://yastatic.net/q/logoaas/v2/Яндекс.svg?circle=black&color=000&first=white)![Практикум](https://yastatic.net/q/logoaas/v2/Практикум.svg?color=000)

Бот для отслеживания статуса код-ревью проектов Яндекс.Практикум.

Каждые 10 минут бот проверяет API Яндекс.Практикум. Если статус проверки изменился, сообщение будет отправлено в телеграм, также бот логирует ошибки и отправляет сообщение.

***
_Репозиторий на Github [ссылка](https://github.com/JuliaBars/homework_bot)._
***

## Технологии

- Python
- Python-telegram-bot

### Установка

- Для использования API Практикум.Домашка необходимо получить токен по адресу: [ссылка](https://oauth.yandex.ru/verification_code#access_token=y0_AgAAAAAOfSqaAAYckQAAAADY4xxHceeHbWerTrqNqg4k_plqLNOW8qg&token_type=bearer&expires_in=1719905)

```
git clone <ссылка>
```

- Установите и активируйте виртуальное окружение
- Установите зависимости из файла requirements.txt

```
pip install -r requirements.txt
```

В файл .env добавляем токены:

```
PRACTICUM_TOKEN=токен API Практикум.Домашка
TELEGRAM_TOKEN=ваш телеграм токен
TELEGRAM_CHAT_ID=телеграм токен вашего бота
```

- В папке с файлом manage.py выполните команду:

```
python homework.py
```

### Автор

Студент Я.Практикум - _Юлия Орлова_
