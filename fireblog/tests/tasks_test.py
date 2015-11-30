from fireblog.tasks import reload_uwsgi
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path
try:
    import unittest.mock as mock
except ImportError:
    import mock  # python3.2 support


@mock.patch('fireblog.tasks.uwsgi')
@mock.patch('time.sleep')
def test_reload_func_removes_all_files_in_spooler_dir(_, __, tmpdir):
    tmpdir = Path(str(tmpdir))
    for file in ['test1', 'test2', 'test3']:
        (tmpdir/file).touch()
    reload_uwsgi(dict(spooler_dir=str(tmpdir)))
    assert len([x for x in tmpdir.iterdir()]) == 0


@mock.patch('fireblog.tasks.uwsgi')
@mock.patch('time.sleep')
def test_reload_func_doesnt_remove_folders_in_spooler_dir(_, __, tmpdir):
    tmpdir = Path(str(tmpdir))
    for file in ['test1', 'test2', 'test3']:
        (tmpdir/file).touch()
    # Create a directory with a file in it
    test_dir = tmpdir/'test_dir'
    test_dir.mkdir()
    (test_dir/'test4').touch()
    reload_uwsgi(dict(spooler_dir=str(tmpdir)))
    # Only the directory should remain, all the files should have been deleted.
    assert [x for x in tmpdir.iterdir()] == [test_dir]


@mock.patch('fireblog.tasks.uwsgi')
@mock.patch('time.sleep')
def test_reload_func_sleeps_for_one_second(sleep_mock, __, tmpdir):
    reload_uwsgi(dict(spooler_dir=str(tmpdir)))
    sleep_mock.assert_called_once_with(1)


@mock.patch('fireblog.tasks.uwsgi')
@mock.patch('time.sleep')
def test_reload_func_calls_uwsgi_reload_func(_, uwsgi_mock, tmpdir):
    reload_uwsgi(dict(spooler_dir=str(tmpdir)))
    uwsgi_mock.reload.assert_called_once_with()
