from bs4 import BeautifulSoup
import requests
import pytest

from .exceptions import ArticleNotFound
from .html_tools import remove_buzz_attrs, remove_buzz_tags


def sanitize(html):
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.select("article.article")

    if len(articles) != 1:
        raise ArticleNotFound()

    article = articles[0]

    buzz_blocks = [
        *article.select('.article-disclaimer'),
        *article.select('footer.article-footer'),
        *article.select('aside'),
    ]
    for el in buzz_blocks:
        el.decompose()

    remove_buzz_attrs(article)
    remove_buzz_tags(article)

    text = article.prettify()
    return text.strip()


def test_sanitize():
    resp = requests.get('https://inosmi.ru/economic/20190629/245384784.html')
    resp.raise_for_status()
    clean_text = sanitize(resp.text)

    assert clean_text.startswith('<article')
    assert clean_text.endswith('</article>')
    assert 'В субботу, 29 июня, президент США Дональд Трамп' in clean_text
    assert 'За несколько часов до встречи с Си' in clean_text

    assert '<img src="' in clean_text
    assert '<a href="' in clean_text
    assert '<h1>' in clean_text


def test_sanitize_wrong_url():
    resp = requests.get('http://example.com')
    resp.raise_for_status()
    with pytest.raises(ArticleNotFound):
        sanitize(resp.text)
