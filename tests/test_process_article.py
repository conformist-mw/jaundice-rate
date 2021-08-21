from functools import partial

import aiohttp
import pymorphy2
import pytest

import process_article
from utils import load_charged_dicts

pytestmark = pytest.mark.process_article


@pytest.fixture(scope='session')
def morph():
    return pymorphy2.MorphAnalyzer()


@pytest.fixture()
async def session():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture(scope='session')
def charged_words():
    return load_charged_dicts()


@pytest.fixture()
def results():
    return []


@pytest.fixture()
async def process(morph, session, charged_words, results):
    return partial(
        process_article.process_article,
        session,
        charged_words,
        morph,
        results,
    )


@pytest.mark.asyncio()
async def test_process_status_parsing_error(process, results):
    process_article.TIMEOUT = 10
    url = 'https://lenta.ru/news/2021/08/20/rogozin_vyzov/'
    await process(url)
    assert 1 == len(results)
    result = results[0]
    assert 'PARSING_ERROR' == result['status']


@pytest.mark.asyncio()
async def test_process_status_is_ok(process, results):
    url = 'https://inosmi.ru/politic/20210820/250347187.html'
    await process(url)
    assert 1 == len(results)
    result = results[0]
    assert 'OK' == result['status']


@pytest.mark.asyncio()
async def test_process_status_fetch_error(process, results):
    url = 'https://inosmi.ru/NOT_EXISTS'
    await process(url)
    assert 1 == len(results)
    result = results[0]
    assert 'FETCH_ERROR' == result['status']


@pytest.mark.asyncio()
async def test_process_status_timeout(process, results):
    url = 'https://inosmi.ru/politic/20210820/250347187.html'
    process_article.TIMEOUT = 0.1
    await process(url)
    assert 1 == len(results)
    result = results[0]
    assert 'TIMEOUT' == result['status']
