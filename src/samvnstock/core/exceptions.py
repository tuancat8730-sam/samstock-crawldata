class SamVnStockError(Exception):
    """Base exception for all samvnstock errors."""


class SourceError(SamVnStockError):
    """Raised when an upstream data source returns an unexpected response."""


class SymbolNotFoundError(SourceError):
    """Raised when a requested symbol cannot be resolved by a provider."""


class RateLimitError(SourceError):
    """Raised when an upstream data source rejects a request due to rate limiting."""


class SourceUnavailableError(SourceError):
    """Raised when an upstream data source is unreachable or returns no usable data."""
