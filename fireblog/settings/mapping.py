from collections import namedtuple
from . import validators

Entry = namedtuple('Entry', [
    'registry_name',  # Registry name
    'display_name',  # Display name
    'description',  # Description
    'type',  # eg int, str...
    # Validator is a function that takes a value and returns a bool
    # indicating if it is a valid entry
    'validator',
    'min',  # If type is a number, then this can be set to the min allowed num
    'max'  # Max allowed num (if type is a number)
])

entry_defaults = (None, None, None, None, object, lambda x: True, None, None)
Entry.__new__.__defaults__ = entry_defaults

mapping = (
    Entry(
        'fireblog.max_rss_items',
        'Max number of RSS items',
        'The maximum number of items to show in the RSS feed. '
        'The latest posts are shown in the RSS feed.',
        int,
        min=1,
        max=99999),
    Entry(
        'fireblog.all_view_post_len',
        'Max length of post preview',
        'Some webpages show previews of several posts. '
        'Here, you can set how long those previews can be.',
        int,
        min=1,
        max=99999),
    Entry(
        'persona.siteName',
        'Site name',
        'Name of the website. If this is changed, then the website should be '
        'restarted at some point in order to update the display of the '
        'sitename in the login screen.',
        str,
        validators.sitename_validator)
)

# This is a convenient way of accessing all registry names
registry_names = (entry.registry_name for entry in mapping)
