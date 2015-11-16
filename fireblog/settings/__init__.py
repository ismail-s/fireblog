from .db_wrapper import settings_dict  # noqa
from .mapping import mapping, registry_names  # noqa
import transaction


def make_sure_all_settings_exist_and_are_valid():
    """Make sure the settings table in the db has the same number of settings
    as it should have. If not, then we go through all the settings that should
    be in it, and make sure they both are in the settings table and are valid.
    For any that aren't valid or don't exist, we get a correct value from the
    user.
    This function should only be run when the web app is starting up, as it
    requests user input from the command line."""
    if len(settings_dict) != len(mapping):
        with transaction.manager:
            for entry in mapping:
                try:
                    value = settings_dict[entry.registry_name]
                    valid, value = validate_value(entry, value)
                    if valid:
                        continue
                except KeyError:
                    pass
                while True:
                    # Get value from user
                    input_str = 'Please provide a value for the setting "{}": '
                    user_val = input(input_str.format(entry.display_name))
                    valid, value = validate_value(entry, user_val)
                    if valid:
                        break
                    print('That value is invalid.')
                settings_dict[entry.registry_name] = value


def validate_value(entry, value):
    if not value:
        return False, None
    try:
        value = entry.type(value)
    except Exception:
        return False, None
    if not entry.validator(value):
        return False, None
    if entry.min and entry.min > value:
        return False, None
    if entry.max and entry.max < value:
        return False, None
    return True, value


def includeme(config):
    config.add_route('settings', '/settings')
