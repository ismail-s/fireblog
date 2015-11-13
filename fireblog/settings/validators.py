def sitename_validator(item: str):
    return 1 <= len(item) <= 100

def recaptcha_secret_validator(item: str):
    # This is subject to Google changing the len of the recaptcha secret.
    return len(item) == 40