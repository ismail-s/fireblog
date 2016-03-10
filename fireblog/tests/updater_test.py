import fireblog.updater as updater
from fireblog.compat import Path
from git import Repo
import pytest


pytestmark = pytest.mark.usefixtures("test_with_one_theme")


class Test_update_blog_views:

    @staticmethod
    def monkeypatch_updater_funcs(
            monkeypatch, upgrade_required, db_upgrade_required):
        monkeypatch.setattr(
            'fireblog.updater.an_update_is_available',
            lambda: upgrade_required)
        monkeypatch.setattr(
            'fireblog.updater.db_upgrade_is_required',
            lambda: db_upgrade_required)

    def test_GET_update_available_and_no_db_upgrade(
            self, pyramid_config, pyramid_req, monkeypatch):
        self.monkeypatch_updater_funcs(monkeypatch, True, False)
        res = updater.check_for_updates(pyramid_req)
        correct_res = {'save_url': 'http://example.com/check_for_updates',
                       'db_upgrade_required': False,
                       'update_available': True}
        assert res == correct_res

    def test_GET_update_available_and_db_upgrade(
            self, pyramid_config, pyramid_req, monkeypatch):
        self.monkeypatch_updater_funcs(monkeypatch, True, True)
        res = updater.check_for_updates(pyramid_req)
        correct_res = {'save_url': 'http://example.com/check_for_updates',
                       'db_upgrade_required': True,
                       'update_available': True}
        assert res == correct_res

    def test_GET_update_not_available(
            self, pyramid_config, pyramid_req, monkeypatch):
        self.monkeypatch_updater_funcs(monkeypatch, False, False)
        res = updater.check_for_updates(pyramid_req)
        correct_res = {'save_url': 'http://example.com/check_for_updates',
                       'db_upgrade_required': False,
                       'update_available': False}
        assert res == correct_res

    def test_POST_calls_right_func_and_redirects_correctly(
            self, pyramid_config, pyramid_req, monkeypatch):
        def mock_func():
            mock_func.called = True
        monkeypatch.setattr(
            'fireblog.updater.update_to_latest_version',
            mock_func)
        res = updater.update_blog(pyramid_req)
        assert res.location == 'http://example.com/reload'
        assert mock_func.called


class Test_git_related_funcs:

    def set_up(self, tmpdir, monkeypatch):
        # Create local/remote git repos
        local = tmpdir.mkdir('local')
        local_repo = Repo.init(str(local))
        remote = tmpdir.mkdir('remote')
        remote_repo = Repo.init(str(remote))
        # Monkeypatch code being tested
        monkeypatch.setattr('fireblog.updater.repo', local_repo)
        monkeypatch.setattr('fireblog.updater.repo_dir', Path(str(local)))
        monkeypatch.setattr('fireblog.updater.git', local_repo.git)
        monkeypatch.setattr(
            'fireblog.updater._get_current_alembic_revisions',
            lambda: ['first'])
        # Create commit on remote
        remote.join('first').write('test')
        (remote / 'alembic' / 'versions' / 'first.py').write('''revision = 'first'
down_revision = None''', ensure=True)
        remote_repo.index.add(['first', 'alembic/versions/first.py'])
        remote_repo.index.commit('First commit')
        # Add remote to local one
        local_repo.create_remote('origin', str(remote))
        # pull into local, set upstream branch
        local_repo.remotes.origin.pull('master')
        local_repo.branches.master.set_tracking_branch(
            local_repo.remotes.origin.refs.master)
        # Now we have a local and remote repo, with the same commit on both,
        # and the local repo has a remote to the remote repo.
        return local, local_repo, remote, remote_repo

    def test_update_is_available(self, tmpdir, monkeypatch):
        _, _, remote, remote_repo = self.set_up(tmpdir, monkeypatch)
        # Create a commit on remote repo
        remote.join('first').write('test1')
        remote_repo.index.add(['first'])
        remote_repo.index.commit('Second commit')
        assert updater.an_update_is_available()

    def test_update_is_not_available(self, tmpdir, monkeypatch):
        self.set_up(tmpdir, monkeypatch)
        assert not updater.an_update_is_available()

    def test_update_is_not_available_due_to_divergence(
            self, tmpdir, monkeypatch):
        local, local_repo, remote, remote_repo = self.set_up(
            tmpdir, monkeypatch)
        # Add commits to both repos
        local.join('first').write('test1')
        local_repo.index.add(['first'])
        local_repo.index.commit('Second commit')
        remote.join('first').write('Conflict')
        remote_repo.index.add(['first'])
        remote_repo.index.commit('Conflict commit')
        assert not updater.an_update_is_available()

    def test_can_update_to_latest_code(self, tmpdir, monkeypatch):
        _, local_repo, remote, remote_repo = self.set_up(tmpdir, monkeypatch)
        # Create a commit on remote repo
        remote.join('first').write('test1')
        remote_repo.index.add(['first'])
        remote_repo.index.commit('Second commit')

        assert local_repo.head.object != remote_repo.head.object
        updater.update_to_latest_version()
        assert local_repo.head.object == remote_repo.head.object

    def test_db_upgrade_not_required(self, tmpdir, monkeypatch):
        _, _, remote, remote_repo = self.set_up(
            tmpdir, monkeypatch)
        remote.join('first').write('test1')
        remote_repo.index.add(['first'])
        remote_repo.index.commit('Second commit')
        assert updater.an_update_is_available()
        assert not updater.db_upgrade_is_required()

    def test_db_upgrade_required(self, tmpdir, monkeypatch):
        _, _, remote, remote_repo = self.set_up(
            tmpdir, monkeypatch)
        remote.join('first').write('test1')
        (remote / 'alembic' / 'versions' / 'second.py').write(
            '''revision = 'second'
down_revision = 'first\'''', ensure=True)
        remote_repo.index.add(['first', 'alembic/versions/second.py'])
        remote_repo.index.commit('Second commit')
        assert updater.an_update_is_available()
        assert updater.db_upgrade_is_required()

    def test_db_upgrade_required_cant_exec_alembic_files(
            self, tmpdir, monkeypatch):
        _, _, remote, remote_repo = self.set_up(
            tmpdir, monkeypatch)
        remote.join('first').write('test1')
        (remote / 'alembic' / 'versions' / 'second.py').write(
            '''revision = 'second'
down_revision = 'first'
invalid syntax''', ensure=True)
        remote_repo.index.add(['first', 'alembic/versions/second.py'])
        remote_repo.index.commit('Second commit')
        assert updater.an_update_is_available()
        assert updater.db_upgrade_is_required()

    def test_db_upgrade_not_required_but_new_invalid_alembic_file_exists(
            self, tmpdir, monkeypatch):
        _, _, remote, remote_repo = self.set_up(
            tmpdir, monkeypatch)
        remote.join('first').write('test1')
        (remote / 'alembic' / 'versions' / 'second.py').write(
            '''revision = 'second'
down_revision = 'notfirst'
invalid syntax''', ensure=True)
        remote_repo.index.add(['first', 'alembic/versions/second.py'])
        remote_repo.index.commit('Second commit')
        assert updater.an_update_is_available()
        assert not updater.db_upgrade_is_required()

    def test_db_upgrade_not_required_but_new_valid_alembic_file_exists(
            self, tmpdir, monkeypatch):
        _, _, remote, remote_repo = self.set_up(
            tmpdir, monkeypatch)
        remote.join('first').write('test1')
        (remote / 'alembic' / 'versions' / 'second.py').write(
            '''revision = 'second'
down_revision = 'notfirst\'''', ensure=True)
        remote_repo.index.add(['first', 'alembic/versions/second.py'])
        remote_repo.index.commit('Second commit')
        assert updater.an_update_is_available()
        assert not updater.db_upgrade_is_required()


def test_get_current_alembic_revisions(tmpdir, monkeypatch):
    base_dir = tmpdir.mkdir('base')
    # Create alembic.ini
    base_dir.join('alembic.ini').write('[alembic]\n'
                                       'script_location = %(here)s/alembic')
    migration_dir = base_dir / 'alembic' / 'versions'
    # Create 2 revision files, one pointing to the other
    migration_dir.join('first.py').write('''revision = 'first'
down_revision = None''', ensure=True)
    migration_dir.join('second.py').write('''revision = 'second'
down_revision = 'first\'''')
    monkeypatch.setattr('fireblog.updater.repo_dir', Path(str(base_dir)))
    res = updater._get_current_alembic_revisions()
    assert len(res) == 1
    assert res[0] == 'second'
