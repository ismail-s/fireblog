from fireblog.settings.views import Settings
from fireblog.settings import mapping, settings_dict
from pyramid.httpexceptions import HTTPFound
import transaction
import pytest


pytestmark = pytest.mark.usefixtures("test_with_one_theme")


def test_GET_settings(pyramid_config, pyramid_req, theme):
    settings_map = dict((
        ('fireblog.max_rss_items', 100),
        ('fireblog.all_view_post_len', 1000),
        ('persona.siteName', 'sitename'),
        ('persona.secret', 'seekret'),
        ('persona.audiences', 'http://localhost'),
        ('fireblog.recaptcha_secret',
         'secretsecretsecretsecretsecretsecretsecr'),
        ('fireblog.theme', theme)))
    expected_mapping = []
    for entry in mapping:
        new_entry = entry._replace(value=settings_map[entry.registry_name])
        expected_mapping.append(new_entry)
    res = Settings(pyramid_req).settings()
    assert len(res) == 2
    assert res['save_url'] == 'http://example.com/settings'
    assert res['mapping'] == tuple(expected_mapping)


def test_POST_settings_no_errors(pyramid_config, pyramid_req):
    correct_params = [
        ('fireblog.max_rss_items', '52'),
        ('fireblog.all_view_post_len', '100'),
        ('persona.siteName', 'sitename'),
        ('persona.secret', 'seekret'),
        ('persona.audiences', 'http://localhost'),
        ('fireblog.recaptcha_secret',
            'ssssssssssssssssssssssssssssssssssssssss'),
        ('fireblog.theme', 'polymer')]
    pyramid_req.params.update(correct_params)
    with transaction.manager:
        res = Settings(pyramid_req).settings_post()
    assert isinstance(res, HTTPFound)
    assert pyramid_req.session.peek_flash() == []
    for key, value in correct_params:
        assert str(settings_dict[key]) == value


def test_POST_settings_some_errors(pyramid_config, pyramid_req, monkeypatch):
    params_with_some_errors = [
        ('fireblog.max_rss_items', '99999999'),
        ('fireblog.all_view_post_len', '100'),
        ('persona.siteName', ''),
        ('persona.secret', 'seekret'),
        ('persona.audiences', 'http://localhost'),
        ('fireblog.recaptcha_secret',
            'ssssssssssssssssssssssssssssssssssssssss'),
        ('fireblog.theme', 'polymer')]
    pyramid_req.params.update(params_with_some_errors)
    mock_settings_dict = {}
    monkeypatch.setattr('fireblog.settings.settings_dict', mock_settings_dict)
    with transaction.manager:
        res = Settings(pyramid_req).settings_post()
    assert isinstance(res, HTTPFound)
    expected_errors = [
        'Max number of RSS items is too large '
        '(it should be smaller than 99999)',
        '"Site name" setting was not provided, and is required.']
    assert pyramid_req.session.peek_flash() == expected_errors
    assert mock_settings_dict == {}


def test_POST_settings_all_errors(pyramid_config, pyramid_req, monkeypatch):
    params_with_all_errors = [
        ('fireblog.max_rss_items', '99999999'),
        ('fireblog.all_view_post_len', '0'),
        ('persona.siteName', ''),
        ('persona.secret', ''),
        ('persona.audiences', ''),
        ('fireblog.recaptcha_secret',
            'sssssssssssssssssssssssssssssssssssssssss'),
        ('fireblog.theme', 'Polymer')]
    pyramid_req.params.update(params_with_all_errors)
    mock_settings_dict = {}
    monkeypatch.setattr('fireblog.settings.settings_dict', mock_settings_dict)
    with transaction.manager:
        res = Settings(pyramid_req).settings_post()
    assert isinstance(res, HTTPFound)
    expected_errors = [
        'Max number of RSS items is too large '
        '(it should be smaller than 99999)',
        'Max length of post preview is too small (it should be bigger than 1)',
        '"Site name" setting was not provided, and is required.',
        '"Persona secret" setting was not provided, and is required.',
        '"Persona audiences" setting was not provided, and is required.',
        'Recaptcha secret is invalid.',
        'Blog theme is invalid.']
    assert pyramid_req.session.peek_flash() == expected_errors
    assert mock_settings_dict == {}
