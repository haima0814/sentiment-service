from collections import defaultdict
from functools import lru_cache
from typing import Any

import numpy as np
from loguru import logger
from haima.engines.common.research_graph_runtime import ResearchNode
from haima.engines.contract.agent_role import display_agent_name
from haima.engines.contract.evidence import EvidenceRecord
from haima.engines.contract.section_definitions import get_insight_routing_rules, SECTION_DEFINITIONS
from haima.engines.contract.settings import get_settings
from haima.engines.insight_agent.state import InsightState


class SectionEvidenceRoutingNode(ResearchNode):
    """将重排证据按规则或语义相似度路由到固定章节"""

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        """根据配置选择规则或语义方式路由证据"""
        agent_name = display_agent_name(self.context.role)
        logger.info(f"{agent_name} 开始为章节选择证据")

        records = list(state.get("records_by_id").values())
        if _is_semantic_enabled(records):
            section_record_ids = _route_by_semantics(records)
        else:
            section_record_ids = _route_by_rules(records)

        logger.info(f"{agent_name} 章节候选证据完成")
        return {"section_record_ids": section_record_ids}


def _is_semantic_enabled(records: list[EvidenceRecord]) -> bool:
    """判断当前证据是否启用语义路由"""
    settings = get_settings()
    return (
            bool(records)
            and settings.INSIGHT_SEMANTIC_ROUTING_ENABLED
            and bool(settings.INSIGHT_SEMANTIC_ROUTING_MODEL)
    )


def _route_by_semantics(records: list[EvidenceRecord]) -> dict[str, list[str]]:
    """逐条计算与固定章节向量的相似度，并路由到最相似章节 todo 这里匹配规则值得研究"""
    contents = [
        (
            f"{' '.join(record.retrieval.matched_queries)}"
            f"{record.document.content}"
        ).strip() for record in records
    ]

    record_vectors = _get_embedding_model().encode(
        contents,
        normalize_embeddings=True
    )
    section_keys, section_vectors = _get_section_vectors()
    similarities = np.dot(record_vectors, section_vectors.T)
    best_indices = np.argmax(similarities, axis=1)  # 每个record只匹配一条section
    section_record_ids: dict[str, list[str]] = defaultdict(list)
    for record, best_indx in zip(records, best_indices):
        section_key = section_keys[best_indx]
        section_record_ids[section_key].append(record.id)

    return section_record_ids


def _route_by_rules(records: list[EvidenceRecord]) -> dict[str, list[str]]:
    """按关键词规则将证据路由到首个匹配章节"""
    section_record_ids: dict[str, list[str]] = defaultdict(list)
    rules = get_insight_routing_rules()  # key:insight_routing_keywords
    for record in records:
        text = (
            f"{' '.join(record.retrieval.matched_queries)}"
            f"{record.document.content}"
        )
        section_key = next(
            (
                section_key
                for section_key, keywords in rules.items()
                if any(keyword in text for keyword in keywords)
            ),
            None
        )
        if section_key is not None:
            section_record_ids[section_key].append(record.id)
    return section_record_ids


@lru_cache
def _get_embedding_model():
    """惰性加载章节语义路由使用的嵌入模型"""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(str(get_settings().INSIGHT_SEMANTIC_ROUTING_MODEL))


@lru_cache
def _get_section_vectors():
    """缓存固定章节关键词的归一化向量"""
    rules = get_insight_routing_rules()
    section_texts = [
        f"{SECTION_DEFINITIONS[section_key].title}:{' '.join(keywords)}"
        for section_key, keywords in rules.items()
    ]
    section_vectors = _get_embedding_model().encode(
        section_texts,
        normalize_embeddings=True
    )
    section_keys = list(rules.keys())
    return section_keys, section_vectors
