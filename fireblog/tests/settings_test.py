from fireblog.settings import settings

def test_can_set_an_item_and_then_get_the_same_item(pyramid_config):
    assert not settings.get('test', None)
    settings['test'] = 'test_str'
    assert settings['test'] == 'test_str'

def test_changing_an_item_and_getting_it_returns_new_item(pyramid_config):
    settings['test'] = 'test_str'
    settings['test'] = 'test_str1'
    assert settings['test'] == 'test_str1'
