from .db_wrapper import settings_dict  # noqa
from .mapping import mapping, registry_names  # noqa


def includeme(config):
    config.add_route('settings', '/settings')
