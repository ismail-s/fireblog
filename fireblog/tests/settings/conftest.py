import pytest
from fireblog.settings import settings_dict
import transaction


@pytest.yield_fixture
def clear_settings_dict():
    '''
    Sets the settings_dict to be empty for the duration of the test,
    then repopulates it as it was before the test.'''
    cached_dict = {}
    for key, val in settings_dict.items():
        cached_dict[key] = val
    with transaction.manager:
        for key in cached_dict.keys():
            del settings_dict[key]
    yield
    with transaction.manager:
        for key, val in cached_dict.items():
            settings_dict[key] = val
