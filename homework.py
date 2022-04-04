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
from exceptions import *

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 60
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
)
handler.setFormatter(formatter)


def send_message(bot, message):
    """Отправка сообщения в Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logger.error(f'Сбой при отправке сообщения в Telegram: {error}')


def get_api_answer(current_timestamp):
    """Получение ответа API."""
    timestamp = current_timestamp or int(time.time())
    #params = {'from_date': 1646092800}
    params = {'from_date': timestamp}
    try:
        api_answer = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if not api_answer.status_code // 100 == 2:
            raise BadStatusCode
    except requests.exceptions.RequestException as ex:
        logger.error(f'Ошибка при запросе к основному API: {ex}')
    else:
        return api_answer.json()


def check_response(response):
    """Проверяет ответ API и возвращает список домашних работ."""
    if type(response) is not dict:
        raise TypeError('Ответ не является словарем')
    if response['homeworks'] == None:
        raise KeyError('Ответ не содержит ключ homeworks')
    if type(response['homeworks']) is not list:
        raise TypeError('Домашка не возвращается в виде списка')
    return response['homeworks']
    #try:
    #    homeworks_list = response['homeworks']
    #except KeyError as ex:
    #    raise BadResponse(ex)
    #else:
    #    return homeworks_list


def parse_status(homework):
    logger.debug(f'На входе в parse_status: {homework}')
    homework_name = homework['homework_name']
    logger.debug(f'Название домашки: {homework_name}')
    homework_status = homework['status']
    logger.debug(f'Статус домашки: {homework_status}')
    verdict = HOMEWORK_STATUSES[homework_status]
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
            message = parse_status(check[0])
            logger.debug(f'Ответ parse_status: {message}')
            send_message(bot, message)

            current_timestamp = response['current_date']
            time.sleep(RETRY_TIME)
        except BadResponse:
            logger.error(f'В ответе API отсутствует ожидаемый ключ: homeworks')
        except BadStatusCode:
            logger.error(f'API возвращает код, отличный от 200')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
