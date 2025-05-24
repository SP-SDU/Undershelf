from unittest.mock import patch

import pytest

from src.business_logic.aspects import (
    error_handler,
    input_validator,
    method_logger,
    performance_monitor,
    simple_cache,
    validate_non_empty_string,
    validate_positive_int,
)


def test_performance_monitor():
    """Test that performance_monitor decorator preserves function behavior."""

    @performance_monitor
    def sample_function(x):
        return x * 2

    # Test normal execution
    assert sample_function(5) == 10


def test_method_logger():
    """Test that method_logger decorator preserves function behavior."""

    @method_logger
    def sample_function(x):
        return x * 2

    # Test normal execution
    assert sample_function(5) == 10


@patch("src.business_logic.aspects.cache")
def test_simple_cache(mock_cache):
    """Test that simple_cache decorator uses cache appropriately."""
    # Set up cache miss first
    mock_cache.get.return_value = None

    @simple_cache()
    def sample_function(x):
        return x * 2

    # Test cache miss (function should be called)
    result1 = sample_function(5)
    assert result1 == 10
    mock_cache.get.assert_called_once()
    mock_cache.set.assert_called_once()

    # Reset mocks for cache hit
    mock_cache.reset_mock()
    mock_cache.get.return_value = 20  # Simulate cached value

    # Test cache hit (function should not be called)
    result2 = sample_function(5)
    assert result2 == 20  # Should return the cached value
    mock_cache.get.assert_called_once()
    assert not mock_cache.set.called


def test_error_handler():
    """Test that error_handler decorator handles exceptions properly."""

    # Test with default fallback (None)
    @error_handler()
    def failing_function():
        raise ValueError("Test error")

    assert failing_function() is None

    # Test with custom fallback
    fallback_value = {"status": "error"}

    @error_handler(fallback=fallback_value)
    def another_failing_function():
        raise ValueError("Test error")

    assert another_failing_function() is fallback_value

    # Test normal execution
    @error_handler()
    def normal_function(x):
        return x * 2

    assert normal_function(5) == 10


def test_input_validator():
    """Test that input_validator executes validators before function."""

    @input_validator(validate_positive_int)
    def sample_function(obj, num):
        return num * 2

    # Test valid input
    assert sample_function(None, 5) == 10

    # Test invalid input
    with pytest.raises(ValueError):
        sample_function(None, -5)


def test_validate_positive_int():
    """Test that validate_positive_int properly validates integers."""
    # Valid cases
    validate_positive_int((None, 1, 2), {})
    validate_positive_int((None,), {"max_results": 5})

    # Invalid cases
    with pytest.raises(ValueError):
        validate_positive_int((None, -1), {})

    with pytest.raises(ValueError):
        validate_positive_int((None,), {"max_results": -5})


def test_validate_non_empty_string():
    """Test that validate_non_empty_string properly validates strings."""
    # Valid cases
    validate_non_empty_string((None, "test"), {})
    validate_non_empty_string((None,), {"text": "sample"})

    # Invalid cases
    with pytest.raises(ValueError):
        validate_non_empty_string((None, ""), {})

    with pytest.raises(ValueError):
        validate_non_empty_string((None,), {"text": "  "})
