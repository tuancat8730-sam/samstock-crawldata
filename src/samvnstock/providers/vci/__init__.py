from samvnstock.core.registry import ProviderRegistry
from samvnstock.providers.vci.company import VciCompanyProvider
from samvnstock.providers.vci.listing import VciListingProvider
from samvnstock.providers.vci.quote import VciQuoteProvider

ProviderRegistry.register("listing", "vci", VciListingProvider)
ProviderRegistry.register("quote", "vci", VciQuoteProvider)
ProviderRegistry.register("company", "vci", VciCompanyProvider)

__all__ = ["VciCompanyProvider", "VciListingProvider", "VciQuoteProvider"]
