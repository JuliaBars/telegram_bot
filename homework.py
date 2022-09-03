import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telegram import Bot

from exceptions import EmptyData, HTTPResponseNot200

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


logging.basicConfig(
    level=logging.INFO,
    filename='my_logs.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
handler.setFormatter(formatter)


def send_message(bot, message):
    """Отправка сообщений в Telegram."""
    logging.info(f'Бот {bot} попытался отправить сообщение: {message}')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(f'Сообщение в Телеграм отправлено: {message}')
    except Exception as error:
        logging.error(f'Ошибка отправки сообщения в Telegram: {error}')


def get_api_answer(current_timestamp):
    """Получение ответов с Яндекс.Практикум."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        logging.info(f'Выполнен запрос к API: {response}')
    except Exception as request_error:
        message = (f'Код ответа API: {request_error},'
                   f'детали запроса: {response}')
        logging.error(message)
    if response.status_code != HTTPStatus.OK:
        raise HTTPResponseNot200(message)
    return response.json()


def check_response(response):
    """Проверка корректности ответов API."""
    logging.info(f'Ответ сервера: {response}')
    if not isinstance(response, dict):
        raise TypeError('response не является словарем')
    if not isinstance(response['homeworks'], list):
        raise TypeError('homeworks не является list')
    if 'homeworks' not in response:
        logging.error('ответ API не содержит ключа')
        raise EmptyData('ответ API не содержит ключа')
    if response == []:
        raise EmptyData('Никаких обновлений в статусе нет')

    return response['homeworks']


def parse_status(homework):
    """Проверяем статус ответа API."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES.get(homework_status)

    if not homework_name:
        raise KeyError('Ошибка: нет домашних работ')

    if not homework_status:
        logging.debug('отсутствие в ответе новых статусов')
        raise EmptyData('Ошибка: пустой статус')

    if not verdict:
        logging.error('недокументированный статус домашней работы')
        raise TypeError('недокументированный статус домашней работы')

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяем токены."""
    tokens = {
        'practicum_token': PRACTICUM_TOKEN,
        'telegram_token': TELEGRAM_TOKEN,
        'telegram_chat_id': TELEGRAM_CHAT_ID,
    }
    for key, value in tokens.items():
        if value is None:
            logging.critical(f'{key} отсутствует')
            return False
    return True


def main():
    """Основная логика работы бота."""
    if check_tokens():
        bot = Bot(token=TELEGRAM_TOKEN)
        current_timestamp = int(time.time())
    else:
        sys.exit('Отсутствуют токены переменных окружения')

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if not homeworks:
                logger.debug('Новых статусов по домашним работам нет.')
                send_message(bot, 'Новых статусов нет, но я работаю')
            else:
                message = parse_status(homeworks)
                send_message(bot, message)
            current_timestamp = int(time.time())

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)

        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
