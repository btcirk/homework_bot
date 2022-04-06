import logging
import sys
import os
import time
import requests
import telegram
from dotenv import load_dotenv
from logging import StreamHandler
from http import HTTPStatus

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 10
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
        logger.info(f'Бот отправил сообщение {message}')
    except Exception as error:
        raise Exception(f'Сбой при отправке сообщения в Telegram: {error}')


def get_api_answer(current_timestamp):
    """Получение ответа API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        api_answer = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if api_answer.status_code != HTTPStatus.OK:
            message = (f'Эндпоинт {ENDPOINT} недоступен. '
                       f'Код ответа API: {api_answer.status_code}')
            raise Exception(message)
    except requests.exceptions.RequestException as ex:
        raise Exception(f'Ошибка при запросе к основному API: {ex}')
    else:
        return api_answer.json()


def check_response(response):
    """Проверяет ответ API и возвращает список домашних работ."""
    if not isinstance(response, dict):
        raise TypeError('Ответ не является словарем')
    if 'homeworks' not in response:
        raise KeyError('Ответ не содержит ключ homeworks')
    if not isinstance(response['homeworks'], list):
        raise TypeError('Домашка не возвращается в виде списка')
    return response['homeworks']


def parse_status(homework):
    """Извлекает статус домашней работы.
    Возвращает строку для отправки в Telegram.
    """
    logger.debug(f'На входе в parse_status: {homework}')
    homework_name = homework.get('homework_name')
    logger.debug(f'Название домашки: {homework_name}')
    homework_status = homework.get('status')
    logger.debug(f'Статус домашки: {homework_status}')
    if homework_status not in HOMEWORK_STATUSES:
        raise KeyError('Недокументированный статус домашней '
                       'работы в ответе API')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка доступности переменных окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Основная логика работы бота."""
    if check_tokens() is False:
        logger.critical('Отсутствует обязательная переменная окружения. '
                        'Программа принудительно остановлена.')
        raise SystemExit

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    MESSAGE = ''
    ERROR = ''

    while True:
        try:
            response = get_api_answer(current_timestamp)
            logger.debug(f'Ответ get_api_answer: {response}')
            check = check_response(response)
            if len(check) == 0:
                logger.debug('Список домашек пуст. Подождем ещё.')
                current_timestamp = response['current_date']
                continue
            logger.debug(f'Ответ check_response: {check}')
            message = parse_status(check[0])
            logger.debug(f'Ответ parse_status: {message}')
            if message != MESSAGE:
                send_message(bot, message)
                MESSAGE = message
            else:
                logger.debug('Ответ не изменился. Подождем ещё.')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if message != ERROR:
                send_message(bot, message)
                ERROR = message
        else:
            current_timestamp = response['current_date']
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
