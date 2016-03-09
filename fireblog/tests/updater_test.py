import fireblog.updater as updater


class Test_update_blog_views:
    @staticmethod
    def monkeypatch_updater_funcs(monkeypatch, upgrade_required, db_upgrade_required):
        monkeypatch.setattr('fireblog.updater.an_update_is_available', lambda: upgrade_required)
        monkeypatch.setattr('fireblog.updater.db_upgrade_is_required', lambda: db_upgrade_required)

    def test_GET_update_available_and_no_db_upgrade(self, pyramid_config, pyramid_req, monkeypatch):
        self.monkeypatch_updater_funcs(monkeypatch, True, False)
        res = updater.check_for_updates(pyramid_req)
        correct_res = {'save_url': 'http://example.com/check_for_updates',
        'db_upgrade_required': False,
        'update_available': True}
        assert res == correct_res

    def test_GET_update_available_and_db_upgrade(self, pyramid_config, pyramid_req, monkeypatch):
        self.monkeypatch_updater_funcs(monkeypatch, True, True)
        res = updater.check_for_updates(pyramid_req)
        correct_res = {'save_url': 'http://example.com/check_for_updates',
        'db_upgrade_required': True,
        'update_available': True}
        assert res == correct_res

    def test_GET_update_not_available(self, pyramid_config, pyramid_req, monkeypatch):
        self.monkeypatch_updater_funcs(monkeypatch, False, False)
        res = updater.check_for_updates(pyramid_req)
        correct_res = {'save_url': 'http://example.com/check_for_updates',
        'db_upgrade_required': False,
        'update_available': False}
        assert res == correct_res

    def test_POST_calls_right_func_and_redirects_correctly(self, pyramid_config, pyramid_req, monkeypatch):
        def mock_func(): mock_func.called = True
        monkeypatch.setattr('fireblog.updater.update_to_latest_version', mock_func)
        res = updater.update_blog(pyramid_req)
        assert res.location == 'http://example.com/reload'
        assert mock_func.called
