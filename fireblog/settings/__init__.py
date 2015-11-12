# Imports here make it easier to use this package elsewhere
from .db_wrapper import settings_dict  # noqa
from .mapping import mapping  # noqa


def includeme(config):
    config.add_route('settings', '/settings')
