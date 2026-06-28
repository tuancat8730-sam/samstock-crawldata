from samvnstock.core.registry import ProviderRegistry
from samvnstock.providers.vnd.quote import VndQuoteProvider

ProviderRegistry.register("quote", "vnd", VndQuoteProvider)

__all__ = ["VndQuoteProvider"]
