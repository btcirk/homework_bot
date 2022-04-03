import logging
import sys
import os
import time
import requests
import telegram
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from dotenv import load_dotenv
from logging import StreamHandler
from datetime import datetime, timedelta

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

hw = {}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
)
handler.setFormatter(formatter)


def send_message(bot, message):
    ...


def get_api_answer(current_timestamp):
    """Получение ответа API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': 1646092800}
    try:
        api_answer = requests.get(ENDPOINT, headers=HEADERS, params=params)
        return api_answer.json()
    except Exception as error:
        logger.error(f'Ошибка при запросе к основному API: {error}')


def check_response(response):
    """Проверка корректности ответа API."""
    try:
        return response['homeworks']
    except Exception as error:
        logger.error(f'В ответе API отсутствует ожидаемый ключ: {error}')


def parse_status(homework):
    logger.debug(f'На входе в parse_status: {homework}')
    homework_name = homework['homework_name']
    logger.debug(f'Название домашки: {homework_name}')
    homework_status = homework['status']
    logger.debug(f'Статус домашки: {homework_status}')
    #now = datetime.now()
    now = datetime.strptime('2022-03-09T12:59:59Z', '%Y-%m-%dT%H:%M:%SZ')
    updated = datetime.strptime(homework['date_updated'], '%Y-%m-%dT%H:%M:%SZ')
    logger.debug(f'Время сейчас: {now}')
    logger.debug(f'Время последнего обновления домашки: {updated}')
    logger.debug(f'Разница в обновлении домашки составляет: {now - updated}')
    if (now - updated) > timedelta(minutes=10):
        logger.info(f'Обновлений не было')
        return False
    else:

        ...

        verdict = 'hjgj'

        ...

        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Основная логика работы бота."""
    if check_tokens() == False:
        if not PRACTICUM_TOKEN:
            logger.critical('Отсутствует обязательная переменная окружения: PRACTICUM_TOKEN')
        if not TELEGRAM_TOKEN:
            logger.critical('Отсутствует обязательная переменная окружения: TELEGRAM_TOKEN')
        if not TELEGRAM_CHAT_ID:
            logger.critical('Отсутствует обязательная переменная окружения: TELEGRAM_CHAT_ID')
        logger.critical('Программа принудительно остановлена.')
        raise SystemExit

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            logger.debug(f'Ответ get_api_answer: {response}')
            check = check_response(response)
            logger.debug(f'Ответ check_response: {check}')
            parse = parse_status(check[0])
            logger.debug(f'Ответ parse_status: {parse}')
            ...

            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
