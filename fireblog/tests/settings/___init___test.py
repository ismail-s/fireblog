from fireblog.settings import validate_value
from fireblog.settings.mapping import Entry
from hypothesis import given
import hypothesis.strategies as st


@given(st.none())
def test_validate_value_with_no_value(n):
    valid, val, error_str = validate_value(Entry(), n)
    assert not valid
    assert val == None
    assert len(error_str)

@given(st.one_of(st.text(), st.integers()))
def test_validate_value_with_invalid_type(n):
    def raise_exception(x):
        raise Exception
    entry = Entry(type=raise_exception)
    valid, val, error_str = validate_value(entry, n)
    assert not valid
    assert val == None
    assert len(error_str)


@given(st.one_of(st.text(), st.integers()))
def test_validate_value_which_doesnt_pass_validator_func(n):
    def validator_func(x):
        return False
    entry = Entry(validator=validator_func)
    valid, val, error_str = validate_value(entry, n)
    assert not valid
    assert val == None
    assert len(error_str)


@given(st.integers(max_value=32))
def test_validate_value_which_is_too_small(n):
    entry = Entry(min=33)
    valid, val, error_str = validate_value(entry, n)
    assert not valid
    assert val == None
    assert len(error_str)


@given(st.integers(min_value=34))
def test_validate_value_which_is_too_large(n):
    entry = Entry(max=33)
    valid, val, error_str = validate_value(entry, n)
    assert not valid
    assert val == None
    assert len(error_str)


def test_validate_value_which_is_just_big_enough():
    entry = Entry(min=33, type=int)
    valid, val, error_str = validate_value(entry, '33')
    assert valid
    assert val == 33
    assert not len(error_str)


def test_validate_value_which_is_just_small_enough():
    entry = Entry(max=33, type=int)
    valid, val, error_str = validate_value(entry, '33')
    assert valid
    assert val == 33
    assert not len(error_str)
