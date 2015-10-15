import pytest
import fireblog.models as models
import unittest.mock as mock


class Test_create_username:
    def test_func_called_with_bad_context(self):
        fake_context = mock.Mock()
        fake_context.current_parameters = {}
        with pytest.raises(Exception):
            models.create_username(fake_context)

    def test_func_called_with_non_email_address(self):
        fake_context = mock.Mock()
        fake_context.current_parameters = {'userid': 'notanemail[at]addr.com'}
        with pytest.raises(Exception):
            models.create_username(fake_context)

    def test_func_called_with_valid_unique_userid(self, pyramid_config):
        fake_context = mock.Mock()
        fake_context.current_parameters = {'userid': 'valid@addr.com'}
        res = models.create_username(fake_context)
        assert res == 'valid'

    def test_func_called_with_unique_email_but_existing_userid(self, pyramid_config):
        fake_context = mock.Mock()
        fake_context.current_parameters = {'userid': 'commenter@addr.com'}
        res = models.create_username(fake_context)
        assert res.startswith('commenter')
        assert res != 'commenter'