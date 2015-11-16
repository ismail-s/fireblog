import os


def sitename_validator(item: str):
    return 1 <= len(item) <= 100


def recaptcha_secret_validator(item: str):
    # This is subject to Google changing the len of the recaptcha secret.
    return len(item) == 40


def theme_validator(item: str):
    # Get all available themes
    theme_folder = os.path.join(os.path.dirname(__file__), '../templates')
    themes = next(os.walk(theme_folder))[1]
    return item in themes
