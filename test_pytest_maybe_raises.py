import contextlib
import functools

import pytest


def func_that_raises(value):
    if isinstance(value, str):
        if value:
            raise ValueError(f"Function does not accept the value '{value}'")
        return True
    raise TypeError(f"Type '{type(value).__name__}' is not a valid type for function")


parametrization = pytest.mark.parametrize(
    ("value", "expected_result", "expected_match"),
    (
        ("foo", ValueError, "Function does not accept the value 'foo'"),
        ("", True, None),
        (1, TypeError, "Type 'int' is not a valid type for function"),
        (True, TypeError, "Type 'bool' is not a valid type for function"),
    ),
)


def assert_func_that_raises(value, expected_result):
    result = func_that_raises(value)
    assert result == expected_result
    assert result is not False


@parametrization
def test_branching(value, expected_result, expected_match):
    if hasattr(expected_result, "__traceback__"):
        with pytest.raises(expected_result, match=expected_match) as exc_info:
            func_that_raises(value)
            assert exc_info.type is expected_result
    else:
        assert_func_that_raises(value, expected_result)


@parametrization
def test_without_branching(value, expected_result, expected_match):
    ctx = (
        functools.partial(pytest.raises, match=expected_match)
        if hasattr(expected_result, "__traceback__")
        else contextlib.nullcontext
    )
    with ctx(expected_result) as exc_info_or_result:
        assert_func_that_raises(value, expected_result)

    if isinstance(exc_info_or_result, pytest.ExceptionInfo):
        assert exc_info_or_result.type is expected_result
    else:
        assert exc_info_or_result == expected_result


@parametrization
def test_with_fixture(value, expected_result, expected_match, maybe_raises):
    with maybe_raises(expected_result, match=expected_match) as exc_info_or_result:
        assert_func_that_raises(value, expected_result)

    if isinstance(exc_info_or_result, pytest.ExceptionInfo):
        assert exc_info_or_result.type is expected_result
    else:
        assert exc_info_or_result == expected_result
