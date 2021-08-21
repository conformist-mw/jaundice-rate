import os


def load_charged_dicts():
    charged_words = []
    for filename in os.listdir('charged_dict'):
        with open(os.path.join('charged_dict', filename)) as file:
            charged_words.extend(file.read().splitlines())
    return charged_words
