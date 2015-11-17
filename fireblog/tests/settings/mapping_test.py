from fireblog.settings.mapping import Entry
from hypothesis import given
from hypothesis.strategies import text


def test_Entry_default_none_values():
    e = Entry()
    none_attrs = ('registry_name',
    'display_name',
    'description',
    'min',
    'max',
    'value')
    for attr in none_attrs:
        assert getattr(e, attr) == None

@given(text())
def test_Entry_default_type_is_identity(s):
    assert Entry().type(s) == s


@given(text())
def test_Entry_default_validator_always_returns_true(s):
    assert Entry().validator(s) == True
