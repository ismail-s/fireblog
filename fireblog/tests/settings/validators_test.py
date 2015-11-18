from hypothesis import given
import hypothesis.strategies as st
import fireblog.settings.validators as v


@given(st.text(min_size=1, max_size=100))
def test_sitename_validator_success(s):
    assert v.sitename_validator(s)


@given(st.one_of(st.text(max_size=0), st.text(min_size=101)))
def test_sitename_validator_fail(s):
    assert not v.sitename_validator(s)


@given(st.text(min_size=40, max_size=40))
def test_recaptcha_validator_success(s):
    assert v.recaptcha_secret_validator(s)


@given(st.one_of(st.text(min_size=41), st.text(max_size=39)))
def test_recaptcha_validator_fail(s):
    assert not v.recaptcha_secret_validator(s)


@given(st.sampled_from(('bootstrap', 'polymer')))
def test_theme_validator_success(s):
    assert v.theme_validator(s)


@given(st.text().filter(lambda x: x not in ('bootstrap', 'polymer')))
def test_theme_validator_failure(s):
    assert not v.theme_validator(s)
