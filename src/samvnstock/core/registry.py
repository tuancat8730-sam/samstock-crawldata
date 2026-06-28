class ProviderRegistry:
    """Registry mapping (kind, source) -> provider class.

    `kind` is the data domain ("listing", "quote", ...) and `source` is the
    broker/data source name ("vci", ...). The `api/` facade only talks to
    this registry, never importing a provider module directly — adding a
    new source means registering it here, not touching `api/`.
    """

    _providers: dict[tuple[str, str], type] = {}

    @classmethod
    def register(cls, kind: str, source: str, provider_cls: type) -> None:
        cls._providers[(kind, source.lower())] = provider_cls

    @classmethod
    def get(cls, kind: str, source: str) -> type:
        key = (kind, source.lower())
        if key not in cls._providers:
            available = sorted(s for k, s in cls._providers if k == kind)
            raise ValueError(
                f"Không có provider '{source}' cho '{kind}'. "
                f"Các nguồn khả dụng: {available}"
            )
        return cls._providers[key]

    @classmethod
    def sources_for(cls, kind: str) -> list[str]:
        return sorted(s for k, s in cls._providers if k == kind)

    @classmethod
    def _reset(cls) -> None:
        """Test-only helper to clear registrations between test cases."""
        cls._providers = {}
