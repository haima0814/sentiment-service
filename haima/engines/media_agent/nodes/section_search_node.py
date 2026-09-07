import asyncio
from itertools import zip_longest
from typing import Any

from loguru import logger

from haima.engines.common.research_graph_runtime import ResearchNode, ResearchRunContext
from haima.engines.contract.agent_role import display_agent_name
from haima.engines.contract.evidence import EvidenceRecord
from haima.engines.media_agent.state import MediaState, MediaSectionState
from haima.engines.media_agent.web_search.retrieval_service import MediaRetrievalService


def _merge_query_results(
        query_results:list[list[EvidenceRecord]])->list[EvidenceRecord]:
    selected:list[EvidenceRecord] = []
    seen_ids:set[str] = set()
    ranked_results = [
        sorted(
            records,
            key=lambda record:record.retrieval.channel_scores.get("web_call"),
            reverse=True
        )
        for records in query_results
    ]
    for ranked_records in zip_longest(*ranked_results):
        for record in ranked_records:
            if record is None or record.id in seen_ids:
                continue
            seen_ids.add(record.id)
            selected.append(record)
    return selected     # 每个章节按keywords检索，去重、排序的所有，需要条数可以在这里切片


class SearchNode(ResearchNode):
    """遍历章节组合关键词检索并聚合去重证据"""

    def __init__(self, context: ResearchRunContext):
        """初始化检索节点及媒体检索服务"""
        super().__init__(context)
        self._retrieval_service = MediaRetrievalService()

    async def __call__(self, state:MediaState)->dict[str,Any]:
        agent_name = display_agent_name(self.context.role)
        logger.info(f"{agent_name} 开始执行公域信息搜索")

        query = self.context.query
        sections:list[MediaSectionState] = state.get("sections")
        section_evidence_records = []
        section_queries = []

        for section in sections:
            tool = section.get("search_tool")
            keywords = section.get("search_keywords")
            queries = [f"{query} {keyword}".strip() for keyword in keywords]
            query_results = await asyncio.gather(
                *(self._retrieval_service.retrieve_evidence(tool,search_query)
                for search_query in queries),
            )
            section_records = _merge_query_results(query_results)
            section_evidence_records.append(section_records)
            section_queries.append(
                "\n".join(f"[{tool}] {search_query}" for search_query in queries)
            )
        logger.info(f"{agent_name} 执行公域信息搜索完成")
        return {
            "section_evidence_records": section_evidence_records,
            "section_queries": section_queries,
        }