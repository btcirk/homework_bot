# Бот Telegram

### Описание
Бот Telegram для проверки статуса ревью домашней работы в сервисе Яндекс.Практикум.

### Технологии
Python 3  
requests  
python-telegram-bot  
dotenv  

### Настройка переменных окружения
Создать файл .env, в котором прописать идентификаторы и токены для работы с API Telegram и Яндекс.Домашка:
- Указать свой токен сервиса Практикум.Домашка: 
``` 
PRACTICUM_TOKEN=XXXXX...
```
- Указать API-токен бота Telegram (узнать у @BotFather):
```
TELEGRAM_TOKEN=5219885643:AAGxxx...
```
- Указать идентификатор Telegram, на который бот будет слать сообщения (узнать у @userinfobot): 
```
TELEGRAM_CHAT_ID=123456789
```

### Как запустить проект
- Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

```
python3 -m pip install --upgrade pip
```

- Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

- Запустить бота:
```
python homework.py
```

### API Практикум.Домашка
У API Практикум.Домашка есть лишь один эндпоинт: https://practicum.yandex.ru/api/user_api/homework_statuses/ и доступ к нему возможен только по токену. Получить токен можно по адресу: https://oauth.yandex.ru/authorize?response_type=token.

С помощью API можно получить список домашних работ, статус которых изменился за период от from_date до настоящего момента.

Для успешного запроса нужно:
- в заголовке запроса передать токен авторизации `Authorization: OAuth <token>`  
- в GET-параметре from_date передать метку времени в формате Unix time.

Пример запроса: https://practicum.yandex.ru/api/user_api/homework_statuses/?from_date=1549962000.

### Telegram Bot API
Bot API служит для управления ботами в Telegram. Документация по Bot API опубликована [здесь](https://core.telegram.org/bots/api).
