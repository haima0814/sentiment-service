from haima.engines.media_agent.web_search.base import BaseSearchClient
from haima.engines.media_agent.web_search.provider.anspire_client import AnspireSearchClient
from haima.engines.media_agent.web_search.search_results import SearchProviderResponse


class WebSearchClient:

    def __init__(self):
        self._client:BaseSearchClient = AnspireSearchClient()

    async def comprehensive_search(self,query:str)->SearchProviderResponse:
        """委托具体 Provider 执行综合检索"""
        return await self._client.comprehensive_search(query)

    async def source_search(self, query: str) -> SearchProviderResponse:
        """委托具体 Provider 执行溯源检索"""
        return await self._client.source_search(query)

    async def realtime_search(self, query: str) -> SearchProviderResponse:
        """委托具体 Provider 执行实时检索"""
        return await self._client.realtime_search(query)