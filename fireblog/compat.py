# flake8: noqa
try:
    from pathlib import Path
except ImportError:  # pragma: no cover
    from pathlib2 import Path

try:
    import unittest.mock as mock
except ImportError:  # pragma: no cover
    import mock  # python3.2 support

try:
    from collections.abc import MutableMapping
except ImportError:  # pragma: no cover
    from collections import MutableMapping
