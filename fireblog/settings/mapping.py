from collections import namedtuple
from . import validators

Entry = namedtuple('Entry', [
    'registry_name',  # Registry name
    'display_name',  # Display name
    'description',  # Description
    'type',  # eg int, str... A func that returns an obj of the right type.
    # Validator is a function that takes a value and returns a bool
    # indicating if it is a valid entry
    'default_value',  # A default value that satisfies validator. This means
    # that code that depends on a setting always has some value to use, even
    # if the user hasn't changed the setting yet.
    'validator',
    'min',  # If type is a number, then this can be set to the min allowed num
    'max',  # Max allowed num (if type is a number)
    'value'  # If we know the value of this, then we set this to it.
])

entry_defaults = (None,) * 3 + (lambda x: x, '', lambda x: True) + (None,) * 3
Entry.__new__.__defaults__ = entry_defaults

mapping = (
    Entry(
        'fireblog.max_rss_items',
        'Max number of RSS items',
        'The maximum number of items to show in the RSS feed. '
        'The latest posts are shown in the RSS feed.',
        int,
        default_value=50,
        min=1,
        max=99999),
    Entry(
        'fireblog.all_view_post_len',
        'Max length of post preview',
        'Some webpages show previews of several posts. '
        'Here, you can set how long those previews can be.',
        int,
        default_value=150,
        min=1,
        max=99999),
    Entry(
        'persona.siteName',
        'Site name',
        'Name of the website. If this is changed, then the website should be '
        'restarted at some point in order to update the display of the '
        'sitename in the login screen.',
        str,
        default_value='My blog',
        validator=validators.sitename_validator),
    Entry(
        'persona.secret',
        'Persona secret',
        'This is a secret required by Mozilla Persona, the authentication '
        'mechanism used on this blog. This should basically be some random '
        'string.',
        str,
        default_value='change this to a random string'),
    Entry(
        'persona.audiences',
        'Persona audiences',
        'This should be a list of domains this blog is served on. This is '
        'required by the Persona authentication mechanism. If a domain is '
        'not on this list, then logins won\'t work from that domain.',
        str,
        # This default_value is a list of urls from which you should be able
        # to login to the website before you have changed this setting.
        # Changing this could mean that the end user has to modify the settings
        # db directly just to login for the first time...
        default_value='http://localhost:8080 https://localhost:8080'),
    Entry(
        'fireblog.recaptcha_secret',
        'Recaptcha secret',
        'The Recaptcha secret used for server-side validation to combat spam. '
        'See https://www.google.com/recaptcha for more details.',
        str,
        default_value='Replace this with your recaptcha secret.',
        validator=validators.recaptcha_validator),
    Entry(
        'fireblog.recaptcha_site_key',
        'Recaptcha site key',
        'The Recaptcha site key that is included in the html Recaptcha widget.'
        ' See https://www.google.com/recaptcha for more details.',
        str,
        default_value='Replace me with your recaptcha site key.',
        validator=validators.recaptcha_validator),
    Entry(
        'fireblog.theme',
        'Blog theme',
        'The theme for this blog.',
        str,
        default_value='bootstrap',
        validator=validators.theme_validator)
)
