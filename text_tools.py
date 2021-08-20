import string

import pymorphy2


def _clean_word(word):
    word = word.replace('«', '').replace('»', '').replace('…', '')
    # FIXME какие еще знаки пунктуации часто встречаются ?
    word = word.strip(string.punctuation)
    return word


def split_by_words(morph, text):
    """Учитывает пунктуацию, регистр и словоформы, выкидывает предлоги."""
    words = []
    for word in text.split():
        cleaned_word = _clean_word(word)
        normalized_word = morph.parse(cleaned_word)[0].normal_form
        if len(normalized_word) > 2 or normalized_word == 'не':
            words.append(normalized_word)
    return words





def calculate_jaundice_rate(article_words, charged_words):
    """Расчитывает желтушность текста.

    Принимает список "заряженных"
    слов и ищет их внутри article_words.
    """
    if not article_words:
        return 0.0

    found_charged_words = [
        word for word in article_words if word in set(charged_words)
    ]

    score = len(found_charged_words) / len(article_words) * 100

    return round(score, 2)


