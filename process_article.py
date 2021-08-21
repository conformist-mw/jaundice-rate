import asyncio
import logging
from contextlib import contextmanager
from enum import Enum
from time import monotonic

import aiohttp
import anyio
import pymorphy2
from async_timeout import timeout

from adapters import SANITIZERS, ArticleNotFoundError
from text_tools import calculate_jaundice_rate, split_by_words
from utils import load_charged_dicts

# noinspection PyArgumentList
logging.basicConfig(
    level=logging.DEBUG,
    format='{asctime} - {levelname} - {message}',
    style='{',
)
logger = logging.getLogger(__file__)
pymorphy2_logger = logging.getLogger('pymorphy2.opencorpora_dict.wrapper')
pymorphy2_logger.disabled = True

TIMEOUT = 3


@contextmanager
def time_it():
    start = monotonic()
    try:
        yield
    finally:
        logger.debug('Analyzed time: %s', round(monotonic() - start, 2))


class ProcessingStatus(Enum):
    OK = 'OK'
    TIMEOUT = 'TIMEOUT'
    FETCH_ERROR = 'FETCH_ERROR'
    PARSING_ERROR = 'PARSING_ERROR'

    def __str__(self):
        return str(self.value)


async def fetch(session, url):
    async with timeout(TIMEOUT):
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()


async def process_article(session, negative_words, morph, results, url):
    words_count = None
    rating = None
    status = ProcessingStatus.OK
    try:
        html = await fetch(session, url)
        with time_it():
            plaintext = SANITIZERS['inosmi_ru'](html, plaintext=True)
            words = await split_by_words(morph, plaintext)
        words_count = len(words)
        rating = calculate_jaundice_rate(words, negative_words)
    except aiohttp.client.ClientResponseError:
        status = ProcessingStatus.FETCH_ERROR
    except ArticleNotFoundError:
        status = ProcessingStatus.PARSING_ERROR
    except asyncio.TimeoutError:
        status = ProcessingStatus.TIMEOUT
    results.append({
        'words_count': words_count,
        'rating': rating,
        'status': status.value,
        'url': url,
    })


async def main(urls):
    charged_words = load_charged_dicts()
    morph = pymorphy2.MorphAnalyzer()

    results = []
    async with aiohttp.ClientSession() as session:
        async with anyio.create_task_group() as task_group:
            for url in urls:
                task_group.start_soon(
                    process_article,
                    session,
                    charged_words,
                    morph,
                    results,
                    url,
                )
    for result in results:
        logger.debug(result)

if __name__ == '__main__':
    urls = (
        'https://inosmi.ru/politic/20210820/250347187.html',
        'https://inosmi.ru/social/20210820/250351260.html',
        'https://inosmi.ru/politic/20210820/250346375.html',
        'https://inosmi.ru/politic/20210820/250347883.html',
        'https://inosmi.ru/social/20210820/250350549.html3434434',
        'https://lenta.ru/news/2021/08/20/rogozin_vyzov/',
    )
    asyncio.run(main(urls))
