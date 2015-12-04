import pytest
import fireblog.renderer_globals as renderer_globals


pytestmark = pytest.mark.usefixtures("test_with_one_theme")


class Test_getusername:

    @pytest.mark.parametrize('email, username', [
        ('id5489746@mockmyid.com', 'id5489746'),
        ('commenter@example.com', 'commenter')
    ])
    def test_success(self, pyramid_config, email, username):
        assert renderer_globals.get_username(email) == username

    def test_failure(self, pyramid_config):
        assert renderer_globals.get_username('nonexistentemail@example.com') == ''