import pytest
from fireblog.settings import settings_dict, mapping


pytestmark = pytest.mark.usefixtures("test_with_one_theme")


def test_can_set_an_item_and_then_get_the_same_item(
        pyramid_config, clear_settings_dict):
    assert not settings_dict.get('test', None)
    settings_dict['test'] = 'test_str'
    assert settings_dict['test'] == 'test_str'


def test_changing_an_item_and_getting_it_returns_new_item(
        pyramid_config, clear_settings_dict):
    settings_dict['test'] = 'test_str'
    assert settings_dict['test'] == 'test_str'
    settings_dict['test'] = 'test_str1'
    assert settings_dict['test'] == 'test_str1'


def test_can_get_default_items(pyramid_config, clear_settings_dict):
    for entry in mapping:
        correct_value = entry.type(entry.default_value)
        assert settings_dict[entry.registry_name] == correct_value


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
    results = set()
    for key in settings_dict:
        results.add(key)
    assert results == set([e.registry_name for e in mapping])


def test_can_iterate_over_added_keys(pyramid_config, clear_settings_dict):
    settings_dict.update({'1': '1', '2': '2', '3': '3'})
    results = set()
    for key in settings_dict:
        results.add(key)
    # Get rid of default keys
    results -= set([e.registry_name for e in mapping])
    assert results == set(['1', '2', '3'])


def test_items_are_returned_once_only(pyramid_config, clear_settings_dict):
    registry_name = mapping[0].registry_name
    settings_dict[registry_name] = 'testing'
    counter = 0
    for key in settings_dict:
        if key == registry_name:
            counter += 1
    assert counter == 1
