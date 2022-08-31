import os
import logging
import telegram
import time
from time import strftime
from telegram import Bot
from http import HTTPStatus

from logging.handlers import RotatingFileHandler

import requests

from dotenv import load_dotenv

load_dotenv(override=True)


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

class HTTPResponseNot200(Exception):
    pass

class UnknownStatus(Exception):
    pass

class EmptyData(Exception):
    pass

class APIProblems(Exception):
    pass


logging.basicConfig(
    level=logging.DEBUG,
    filename='my_logger.log',
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('my_logger.log', maxBytes=50000000, backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)


def send_message(bot, message):
    """Отправка сообщений в Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(f'Ошибка  отправки сообщения в Telegram чат: {error}')


def get_api_answer(current_timestamp):
    """Получение ответов с Яндекс.Практикум."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except requests.ConnectionError as request_error:
        message = f'Код ответа API: {request_error}'
        logger.error(message)
        raise ConnectionError(message)
    return response.json()

def check_response(response):
    """Проверка корректности ответов API."""
    try:
        homeworks = response['homeworks']
        if homeworks is True:
            return homeworks
    except Exception as error:
        if type(response) is not dict:
            raise TypeError('response не является словарем')
        elif response == []:
            raise EmptyData(f'Никаких обновлений в статусе нет')
        elif not response['homeworks']:
            raise EmptyData(f'ответ от API не содержит ключа')
        elif response.status_code != 200:
            raise HTTPResponseNot200('API отвечает с ошибкой')
        logging.error(f'В ответе API ошибки: {error}')



def parse_status(homework):
    homework_name = homework['homework_name']
    homework_status = homework['status']
    try:
        verdict = homework_status
        return f'Изменился статус проверки работы {homework_name}. {verdict}'
    except:
        if homework_status is None:
            raise EmptyData(f'Ошибка: пустой статус')
        if homework_name is None:
            raise EmptyData(f'Никаких обновлений в статусе нет')
    
    


def check_tokens():
    tokens = {
        'practicum_token': PRACTICUM_TOKEN,
        'telegram_token': TELEGRAM_TOKEN,
        'telegram_chat_id': TELEGRAM_CHAT_ID,
    }
    for key, value in tokens.items():
        if value is None:
            logging.error(f'{key} отсутствует')
            return False
    return True


def main():
    """Основная логика работы бота."""
    if check_tokens():
        bot = Bot(token=TELEGRAM_TOKEN)
        current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if not homeworks:
                logger.debug('Новых статусов по домашним работам нет.')
                message = 'Новых статусов по домашним работам нет.'
                send_message(bot, message)
            else:
                message = parse_status(homeworks)
                send_message(bot, message)
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()