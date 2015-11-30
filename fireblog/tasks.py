'Tasks that can be run under the uwsgi spooler.'
# uwsgi python module is added dynamically when the blog is run under uwsgi.
# As a result, this module won't be available for importing during test runs.
try:  # pragma: no cover
    from uwsgidecorators import spool
    import uwsgi
except ImportError:  # pragma: no cover
    uwsgi = {}
    spool = lambda x: x
import time
try:  # pragma: no cover
    from pathlib import Path
except ImportError:  # pragma: no cover
    from pathlib2 import Path


@spool
def reload_uwsgi(args):
    'Waits for a second, then reloads the blog.'
    # Remove all spooler files. This is necessary as this current function
    # doesn't return when it reloads uwsgi, so the spooler file that caused
    # this function to be called won't be deleted, which will result in endless
    # reloads...
    # Note this function gets run in the spooler directory.
    spooler_dir = Path(args.get('spooler_dir', '.')).resolve()
    for file in spooler_dir.iterdir():
        if file.is_file():
            file.unlink()
    # Sleep for a second. This allows the request that called this spool
    # function to return a response ie a webpage before the reload happens
    time.sleep(1)
    uwsgi.reload()
