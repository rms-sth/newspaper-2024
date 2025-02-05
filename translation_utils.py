from django.utils.translation import get_language
from translations import TRANSLATIONS


def get_translation(key, lang=None):
    """
    Fetch the translated message for the given key.
    Defaults to English if the translation is unavailable.
    """
    if lang is None:
        lang = get_language()  # Get the current language
    return TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS["en"].get(key, key))


# # NOTE: Usage of get_translation
# from translation_utils import get_translation
# from translations import COMMENT_LOAD_ERROR

# error_message = get_translation(COMMENT_LOAD_ERROR, lang="ne")
# print(error_message)
