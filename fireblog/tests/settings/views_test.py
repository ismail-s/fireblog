from fireblog.settings.views import Settings
from fireblog.settings import mapping


def test_GET_settings(pyramid_config, pyramid_req, theme):
    settings_map = dict((
        ('fireblog.max_rss_items', 100),
        ('fireblog.all_view_post_len', 1000),
        ('persona.siteName', 'sitename'),
        ('persona.secret', 'seekret'),
        ('persona.audiences', 'http://localhost'),
        ('fireblog.recaptcha-secret',
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
