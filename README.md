# pytest-maybe-raises

Pytest fixture for optional exception testing.

## Documentation

I like to parametrize tests for functions that could accepts different
values. I often find myself writing this type of pattern:

```python
import pytest

@pytest.mark.parametrize(
    ('value', 'expected_result'),
    (
        ('foo', 'bar'),
        ('baz', ValueError)
    )
)
def test_something(value, expected_result):
    if hasattr(expected_result, '__traceback__'):  # is an exception
        with pytest.raises(expected_result):
            my_func(value)
    else:
        result = my_func(value)
        assert result == expected_result
        assert bool(result) 
```

But this is really long and ugly.

Does pytest provides a fixture that allows me to only uses the [`pytest.raises`]
context when the provided argument is an exception class? The answer is not (see
[this question in Stackoverflow](https://stackoverflow.com/q/42623495/9167585)),
so I've written this convenient fixture:

```python
import contextlib
import pytest

@contextlib.contextmanager
def _maybe_raises(maybe_exception_class, *args, **kwargs):
    if hasattr(maybe_exception_class, '__traceback__'):
        with pytest.raises(maybe_exception_class, *args, **kwargs) as exc_info:
            yield exc_info
    else:
        yield maybe_exception_class

@pytest.fixture()
def maybe_raises():
    return _maybe_raises
```

This package provides a wrapper fixture over `pytest.raises` which
context only has effect if the passed argument is an exception class,
otherwise uses a null context like [`contextlib.nullcontext`].

Using this package I can rewrite my tests as:

```python
import pytest

@pytest.mark.parametrize(
    ('value', 'expected_result'),
    (
        ('foo', 'bar'),
        ('baz', ValueError)
    )
)
def test_something(value, expected_result, maybe_raises):
    with maybe_raises(expected_result):
        result = my_func(value)
        assert result == expected_result
        assert bool(result)
```

But in order to use it properly you need to know how the magic works:

Note that when an exception raises inside [`pytest.raises`] context, the
context exits so the later `assert ... == expected_result` comparison
is not executed. If other exception raises would be propagated to your test
so the comparison is not executed either. This allows you to write more
assertions after the execution of the function for successfull calls.

[`pytest.raises`]: https://docs.pytest.org/en/latest/reference/reference.html?highlight=pytest%20raises#pytest-raises
[`contextlib.nullcontext`]: https://docs.python.org/3/library/contextlib.html#contextlib.nullcontext
