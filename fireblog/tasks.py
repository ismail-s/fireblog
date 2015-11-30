from uwsgidecorators import spool
import uwsgi
import time
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path


@spool
def reload_uwsgi(args):
    # Remove all spooler files. This is necessary as this current function
    # doesn't return when it reloads uwsgi, so the spooler file that caused
    # this function to be called won't be deleted, which will result in endless
    # reloads...
    # Note this function gets run in the spooler directory.
    spooler_dir = Path('.').resolve()
    for file in spooler_dir.iterdir():
        if file.is_file():
            file.unlink()
    # Sleep for a second. This allows the request that called this spool
    # function to return a response ie a webpage before the reload happens
    time.sleep(1)
    uwsgi.reload()
