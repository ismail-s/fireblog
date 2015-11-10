import pytest
from fireblog.settings import settings


def test_can_set_an_item_and_then_get_the_same_item(pyramid_config):
    assert not settings.get('test', None)
    settings['test'] = 'test_str'
    assert settings['test'] == 'test_str'


def test_changing_an_item_and_getting_it_returns_new_item(pyramid_config):
    settings['test'] = 'test_str'
    assert settings['test'] == 'test_str'
    settings['test'] = 'test_str1'
    assert settings['test'] == 'test_str1'


def test_can_delete_an_item(pyramid_config):
    settings['test'] = 'test_str'
    assert settings['test']
    del settings['test']
    assert not settings.get('test', None)
    with pytest.raises(KeyError):
        settings['test']


def test_can_get_num_of_settings(pyramid_config):
    settings.update({'1': '1', '2': '2', '3': '3'})
    assert len(settings) == 3
    del settings['3']
    assert len(settings) == 2
    settings['test'] = 'te'
    assert len(settings) == 3


def test_can_iterate_over_keys(pyramid_config):
    settings.update({'1': '1', '2': '2', '3': '3'})
    results = set()
    for key in settings:
        results.add(key)
    assert results == set(['1', '2', '3'])
