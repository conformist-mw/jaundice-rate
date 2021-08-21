import string

from anyio import sleep
from async_timeout import timeout

TIMEOUT = 5


def _clean_word(word):
    word = word.replace('«', '').replace('»', '').replace('…', '')
    # FIXME какие еще знаки пунктуации часто встречаются ?
    word = word.strip(string.punctuation)
    return word


async def split_by_words(morph, text, time_out=TIMEOUT):
    """Учитывает пунктуацию, регистр и словоформы, выкидывает предлоги."""
    words = []
    async with timeout(time_out):
        for word in text.split():
            cleaned_word = _clean_word(word)
            normalized_word = morph.parse(cleaned_word)[0].normal_form
            if len(normalized_word) > 2 or normalized_word == 'не':
                words.append(normalized_word)
            await sleep(0)
    return words


def calculate_jaundice_rate(article_words, charged_words):
    """Рассчитывает желтушность текста.

    Принимает список "заряженных" слов и ищет их внутри article_words.
    """
    if not article_words:
        return 0.0

    found_charged_words = [
        word for word in article_words if word in set(charged_words)
    ]

    score = len(found_charged_words) / len(article_words) * 100

    return round(score, 2)
