from .db_wrapper import settings_dict  # noqa
from .mapping import mapping, Entry  # noqa
import transaction
import logging


log = logging.getLogger(__name__)


def make_sure_all_settings_exist_and_are_valid():
    """Make sure the settings table in the db has the same number of settings
    as it should have. If not, then we go through all the settings that should
    be in it, and make sure they both are in the settings table and are valid.
    For any that aren't valid or don't exist, we get a correct value from the
    user.
    This function is meant to be run as part of a console script, as it uses
    STDIN to get user input, which doesn't work with some app servers eg
    uwsgi."""
    with transaction.manager:
        for entry in mapping:
            try:
                value = settings_dict[entry.registry_name]
                valid, value, _ = validate_value(entry, value)
                if valid:
                    continue
            except KeyError:
                pass
            while True:
                # Get value from user
                input_str = 'Please provide a value for the setting "{}": '
                user_val = input(input_str.format(entry.display_name))
                valid, value, _ = validate_value(entry, user_val)
                if valid:
                    break
                print('That value is invalid.')
            settings_dict[entry.registry_name] = value


def validate_value(entry: Entry, value):
    '''Validate value against entry. If value is invalid, return a tuple made
    up of: valid_or_not, value_if_valid (as correct type), error_str (if there
    were any errors).'''
    invalid_value_str = '{} is invalid.'
    if not value:
        error_str = '"{}" setting was not provided, and is required.'
        error_str = error_str.format(entry.display_name)
        return False, None, error_str
    try:
        value = entry.type(value)
    except Exception:
        error_str = invalid_value_str.format(entry.display_name)
        return False, None, error_str
    if not entry.validator(value):
        error_str = invalid_value_str.format(entry.display_name)
        return False, None, error_str
    if entry.min and entry.min > value:
        error_str = '{} is too small (it should be bigger than {})'
        error_str = error_str.format(entry.display_name, entry.min)
        return False, None, error_str
    if entry.max and entry.max < value:
        error_str = '{} is too large (it should be smaller than {})'
        error_str = error_str.format(entry.display_name, entry.max)
        return False, None, error_str
    return True, value, ''


def includeme(config):
    log.debug('Including settings routes/views')
    config.add_route('settings', '/settings')
