import pytest
import fireblog.models as models
from fireblog.compat import mock


pytestmark = pytest.mark.usefixtures("test_with_one_theme")


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

    def test_func_called_with_existing_userid(self, pyramid_config):
        fake_context = mock.Mock()
        fake_context.current_parameters = {'userid': 'commenter@addr.com'}
        res = models.create_username(fake_context)
        assert res.startswith('commenter')
        assert res != 'commenter'
