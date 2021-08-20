import pytest
import requests

from adapters import ArticleNotFoundError
from adapters.inosmi_ru import sanitize


def test_sanitize():
    resp = requests.get('https://inosmi.ru/economic/20190629/245384784.html')
    resp.raise_for_status()
    clean_text = sanitize(resp.text)

    assert clean_text.startswith('<article>')
    assert clean_text.endswith('</article>')
    assert 'В субботу, 29 июня, президент США Дональд Трамп' in clean_text
    assert 'За несколько часов до встречи с Си' in clean_text

    assert '<img src="' in clean_text
    assert '<a href="' in clean_text
    assert '<h1>' in clean_text

    clean_plaintext = sanitize(resp.text, plaintext=True)

    assert 'В субботу, 29 июня, президент США Дональд Трамп' in clean_plaintext
    assert 'За несколько часов до встречи с Си' in clean_plaintext

    assert '<img src="' not in clean_plaintext
    assert '<a href="' not in clean_plaintext
    assert '<h1>' not in clean_plaintext
    assert '</article>' not in clean_plaintext
    assert '<h1>' not in clean_plaintext


def test_sanitize_wrong_url():
    resp = requests.get('http://example.com')
    resp.raise_for_status()
    with pytest.raises(ArticleNotFoundError):
        sanitize(resp.text)
