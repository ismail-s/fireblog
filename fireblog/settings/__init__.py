from .db_wrapper import settings_dict
from .mapping import mapping


def includeme(config):
    config.add_route('settings', '/settings')
