from fireblog.settings import (
    validate_value,
    make_sure_all_settings_exist_and_are_valid,
    settings_dict
)
from fireblog.settings.mapping import Entry
from hypothesis import given
import hypothesis.strategies as st
import transaction


class Test_get_settings_during_startup:

    def test_gets_and_stores_all_settings_from_command_line(
            self, pyramid_config, clear_settings_dict, monkeypatch, capsys):
        with transaction.manager:
            settings_dict['persona.secret'] = 'somesecret'
        # Setup inputs to be fed in via input func
        inputs = [
            '0', '50', '999999', '500', '', 'sitename', 'http://localhost',
            'x' * 39, 'x' * 40, 'wrong-theme', 'bootstrap']
        input_gen = (i for i in inputs)
        monkeypatch.setattr('builtins.input', lambda prompt: next(input_gen))
        make_sure_all_settings_exist_and_are_valid()
        expected_settings_dict = {
            'fireblog.max_rss_items': 50,
            'fireblog.all_view_post_len': 500,
            'persona.siteName': 'sitename',
            'persona.secret': 'somesecret',
            'persona.audiences': 'http://localhost',
            'fireblog.recaptcha-secret': 'x' * 40,
            'fireblog.theme': 'bootstrap'}
        # Check that settings_dict is all correct
        for key, value in expected_settings_dict.items():
            assert settings_dict[key] == value
        # Check that messages were printed to stdout for each invalid value
        out, err = capsys.readouterr()
        assert not err
        out = [x for x in out.split('\n') if x]
        # 5 Invalid values were supplied
        assert len(out) == 5
        # Check the same message was printed each time.
        assert all((x == out[0] for x in out))


class Test_validate_value:

    @given(st.none())
    def test_validate_value_with_no_value(self, n):
        valid, val, error_str = validate_value(Entry(), n)
        assert not valid
        assert val is None
        assert len(error_str)

    @given(st.one_of(st.text(), st.integers()))
    def test_validate_value_with_invalid_type(self, n):
        def raise_exception(x):
            raise Exception
        entry = Entry(type=raise_exception)
        valid, val, error_str = validate_value(entry, n)
        assert not valid
        assert val is None
        assert len(error_str)

    @given(st.one_of(st.text(), st.integers()))
    def test_validate_value_which_doesnt_pass_validator_func(self, n):
        def validator_func(x):
            return False
        entry = Entry(validator=validator_func)
        valid, val, error_str = validate_value(entry, n)
        assert not valid
        assert val is None
        assert len(error_str)

    @given(st.integers(max_value=32))
    def test_validate_value_which_is_too_small(self, n):
        entry = Entry(min=33)
        valid, val, error_str = validate_value(entry, n)
        assert not valid
        assert val is None
        assert len(error_str)

    @given(st.integers(min_value=34))
    def test_validate_value_which_is_too_large(self, n):
        entry = Entry(max=33)
        valid, val, error_str = validate_value(entry, n)
        assert not valid
        assert val is None
        assert len(error_str)

    def test_validate_value_which_is_just_big_enough(self):
        entry = Entry(min=33, type=int)
        valid, val, error_str = validate_value(entry, '33')
        assert valid
        assert val == 33
        assert not len(error_str)

    def test_validate_value_which_is_just_small_enough(self):
        entry = Entry(max=33, type=int)
        valid, val, error_str = validate_value(entry, '33')
        assert valid
        assert val == 33
        assert not len(error_str)
