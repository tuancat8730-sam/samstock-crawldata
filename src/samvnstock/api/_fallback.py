from collections.abc import Awaitable, Callable
from typing import TypeVar

from samvnstock.core.exceptions import SourceError, SourceUnavailableError

T = TypeVar("T")


def with_fallback(fn: Callable[..., T], sources: list[str], *args: object, **kwargs: object) -> T:
    """Call `fn(*args, source=<s>, **kwargs)` for each `s` in `sources`, in order,
    returning the first successful result.

    Only retries on `SourceError` (an upstream data problem) — programming
    errors (e.g. `TypeError`) still propagate immediately. Intended for
    already-normalized data (Quote/Listing), per
    [[KE-HOACH-CRAWL-DATA-CHI-TIET-1]] section 6.4: don't mix raw reports
    (e.g. Finance) from different sources in one fallback chain.
    """
    last_error: SourceError | None = None
    for source in sources:
        try:
            return fn(*args, source=source, **kwargs)
        except SourceError as exc:
            last_error = exc
            continue
    raise SourceUnavailableError(f"Tất cả nguồn {sources} đều lỗi") from last_error


async def with_fallback_async(
    fn: Callable[..., Awaitable[T]], sources: list[str], *args: object, **kwargs: object
) -> T:
    """Async equivalent of `with_fallback`."""
    last_error: SourceError | None = None
    for source in sources:
        try:
            return await fn(*args, source=source, **kwargs)
        except SourceError as exc:
            last_error = exc
            continue
    raise SourceUnavailableError(f"Tất cả nguồn {sources} đều lỗi") from last_error
