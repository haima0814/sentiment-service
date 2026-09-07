import hashlib
from urllib.parse import urlparse

from haima.engines.contract.evidence import EvidenceRecord, EvidenceDocument, RetrievalMeta
from haima.engines.media_agent.web_search.factory import WebSearchClient
from haima.engines.media_agent.web_search.search_results import SearchTool, SearchProviderResponse


def _extract_source_name(url: str) -> str:
    hostname = urlparse(url).hostname.lower()
    return hostname.removeprefix("www.")


def _generate_content_hash_id(content: str) -> str:
    normalized_content = " ".join(content.strip())
    raw_key = normalized_content.strip()
    return hashlib.md5(raw_key.encode("utf-8")).hexdigest()


def _map_to_evidence_records(response: SearchProviderResponse,
                             query: str) -> list[EvidenceRecord]:
    """将网页结果映射为带稳定哈希 ID 的证据记录"""
    records: list[EvidenceRecord] = []
    for page in response.webpages:
        source_name = _extract_source_name(page.url)
        content = page.content
        url = page.url
        records.append(
            EvidenceRecord(
                document=EvidenceDocument(
                    platform=source_name,
                    source_table="webpage",
                    source_id=_generate_content_hash_id(content),
                    content=content,
                    published_at=page.date,
                    url=url,
                    title=page.title,
                    source_name=source_name
                ),
                retrieval=RetrievalMeta(
                    matched_queries=[query],
                    channel_scores={"web_call": page.score}
                )
            )
        )
    return records


class MediaRetrievalService:

    def __init__(self):
        self._web_search_client = WebSearchClient()

    async def retrieve_evidence(
            self,
            tool_name: SearchTool,
            query: str) -> list[EvidenceRecord]:
        response = await self._search_webpage(tool_name, query)
        return _map_to_evidence_records(response, query)

    async def _search_webpage(self,
                              tool_name: SearchTool,
                              query: str) -> SearchProviderResponse:
        match tool_name:
            case "source_search":
                return await self._web_search_client.source_search(query=query)
            case "realtime_search":
                return await self._web_search_client.realtime_search(query=query)
            case _:
                return await self._web_search_client.comprehensive_search(query=query)



import asyncio

from haima.engines.media_agent.web_search.search_results import SearchTool


async def main() -> None:
    service = MediaRetrievalService()

    query = "孙宇晨"
    tools: list[SearchTool] = ["comprehensive_search", "source_search", "realtime_search"]

    for tool in tools:
        print(f"测试工具: {tool} \n")
        records = await service.retrieve_evidence(tool_name=tool, query=query)

        print(f"共获取 {len(records)} 条证据：\n")
        for i, rec in enumerate(records, start=1):
            doc = rec.document
            score = rec.retrieval.channel_scores.get("web_call")

            print(f"[{i}] 站点: {doc.platform}")
            print(f"    来源: {doc.source_name}")
            print(f"    记录唯一ID: {doc.source_id}")
            print(f"    标题: {doc.title}")
            print(f"    url: {doc.url}")
            print(f"    时间: {doc.published_at}")
            print(f"    得分: {score}")
            print(f"    摘要: {doc.content}...\n")



if __name__ == "__main__":
    asyncio.run(main())