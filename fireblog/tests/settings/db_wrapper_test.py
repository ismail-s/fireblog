import pytest
from fireblog.settings import settings_dict


@pytest.yield_fixture
def clear_settings_dict():
    '''
    Sets the settings_dict to be empty for the duration of the test,
    then repopulates it as it was before the test.'''
    cached_dict = {}
    for key, val in settings_dict.items():
        cached_dict[key] = val
    for key in cached_dict.keys():
        del settings_dict[key]
    yield
    for key, val in cached_dict.items():
        settings_dict[key] = val


def test_can_set_an_item_and_then_get_the_same_item(pyramid_config):
    assert not settings_dict.get('test', None)
    settings_dict['test'] = 'test_str'
    assert settings_dict['test'] == 'test_str'


def test_changing_an_item_and_getting_it_returns_new_item(pyramid_config):
    settings_dict['test'] = 'test_str'
    assert settings_dict['test'] == 'test_str'
    settings_dict['test'] = 'test_str1'
    assert settings_dict['test'] == 'test_str1'


def test_can_delete_an_item(pyramid_config):
    settings_dict['test'] = 'test_str'
    assert settings_dict['test']
    del settings_dict['test']
    assert not settings_dict.get('test', None)
    with pytest.raises(KeyError):
        settings_dict['test']


def test_can_get_num_of_settings(pyramid_config, clear_settings_dict):
    settings_dict.update({'1': '1', '2': '2', '3': '3'})
    assert len(settings_dict) == 3
    del settings_dict['3']
    assert len(settings_dict) == 2
    settings_dict['test'] = 'te'
    assert len(settings_dict) == 3


def test_can_iterate_over_keys(pyramid_config, clear_settings_dict):
    settings_dict.update({'1': '1', '2': '2', '3': '3'})
    results = set()
    for key in settings_dict:
        results.add(key)
    assert results == set(['1', '2', '3'])
