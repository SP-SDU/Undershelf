import functools
import logging
import time
from typing import Any, Callable

from django.core.cache import cache
from django.utils.encoding import force_str

logger = logging.getLogger(__name__)


def performance_monitor(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        name = f"{func.__module__}.{func.__qualname__}"

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            duration = time.time() - start
            logger.error(f"Performance: {name} failed after {duration:.3f}s - {e}")
            raise

        duration = time.time() - start
        logger.info(f"Performance: {name} executed in {duration:.3f}s")
        if duration > 1.0:
            logger.warning(f"Slow operation detected: {name} took {duration:.3f}s")

        return result

    return wrapper


def method_logger(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        name = f"{func.__module__}.{func.__qualname__}"
        logger.debug(f"Entering {name} with params: {_sanitize_params(args, kwargs)}")

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {name}: {e}")
            raise

        logger.debug(f"Exiting {name} - {_summarize_result(result)}")
        return result

    return wrapper


def simple_cache(timeout: int = 300) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = _generate_cache_key(func, args, kwargs)
            cached = cache.get(key)

            if cached is not None:
                logger.debug(f"Cache hit for {func.__qualname__}")
                return cached

            result = func(*args, **kwargs)
            cache.set(key, result, timeout)
            logger.debug(f"Cached result for {func.__qualname__}")
            return result

        return wrapper

    return decorator


def error_handler(fallback: Any = None, propagate=None) -> Callable:
    if propagate is None:
        propagate = []

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                for exc_type in propagate:
                    if isinstance(e, exc_type):
                        raise

                name = f"{func.__module__}.{func.__qualname__}"
                logger.error(f"Error in {name}: {e}")
                logger.info(f"Returning fallback value for {name}")
                return fallback

        return wrapper

    return decorator


def input_validator(*validators: Callable) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name = f"{func.__module__}.{func.__qualname__}"

            for validate in validators:
                try:
                    validate(args, kwargs)
                except Exception as e:
                    logger.warning(f"Validation failed for {name}: {e}")
                    raise ValueError(f"Invalid input: {e}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def _sanitize_params(args: tuple, kwargs: dict) -> dict:
    params = {}

    if len(args) > 1:
        params["args_count"] = len(args) - 1
        for i, arg in enumerate(args[1:], 1):
            if isinstance(arg, (str, int, float, bool)):
                params[f"arg_{i}"] = str(arg)[:100]

    for k, v in kwargs.items():
        if isinstance(v, (str, int, float, bool)):
            params[k] = str(v)[:100]

    return params


def _summarize_result(result: Any) -> str:
    if result is None:
        return "returned None"
    if isinstance(result, (list, tuple)):
        return f"returned {type(result).__name__} with {len(result)} items"
    if isinstance(result, dict):
        return f"returned dict with {len(result)} keys"
    if isinstance(result, str):
        return f"returned string of length {len(result)}"
    return f"returned {type(result).__name__}"


def _generate_cache_key(func: Callable, args: tuple, kwargs: dict) -> str:
    name = f"{func.__module__}.{func.__qualname__}"

    string_args = tuple(map(repr, args))
    string_kwargs = {k: repr(v) for k, v in kwargs.items()}

    param_hash = ""
    if string_args:
        param_hash += str(hash(string_args))
    if string_kwargs:
        param_hash += str(hash(tuple(sorted(string_kwargs.items()))))

    return force_str(f"aop_cache:{name}:{hash(param_hash)}")[:250]


def validate_positive_int(args: tuple, kwargs: dict) -> None:
    for arg in args[1:]:
        if isinstance(arg, int) and arg <= 0:
            raise ValueError("Integer parameters must be positive")

    numeric_keys = {"k", "n_recommendations", "max_results", "max_depth"}
    for key, value in kwargs.items():
        if isinstance(value, int) and key in numeric_keys and value <= 0:
            raise ValueError(f"{key} must be positive")


def validate_non_empty_string(args: tuple, kwargs: dict) -> None:
    for arg in args[1:]:
        if isinstance(arg, str) and not arg.strip():
            raise ValueError("String parameters cannot be empty")

    for key, value in kwargs.items():
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"{key} cannot be empty")
