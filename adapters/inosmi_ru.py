from bs4 import BeautifulSoup

from .exceptions import ArticleNotFoundError
from .html_tools import remove_all_tags, remove_buzz_attrs, remove_buzz_tags


def sanitize(html, plaintext=False):
    soup = BeautifulSoup(html, 'html.parser')
    article = soup.select_one('article.article')

    if not article:
        raise ArticleNotFoundError()

    article.attrs = {}

    buzz_blocks = [
        *article.select('.article-disclaimer'),
        *article.select('footer.article-footer'),
        *article.select('aside'),
    ]
    for el in buzz_blocks:
        el.decompose()

    remove_buzz_attrs(article)
    remove_buzz_tags(article)

    if not plaintext:
        text = article.prettify()
    else:
        remove_all_tags(article)
        text = article.get_text()
    return text.strip()
