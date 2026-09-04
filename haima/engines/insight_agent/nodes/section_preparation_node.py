from typing import Any,Mapping
from loguru import logger

from haima.engines.common.research_graph_runtime import ResearchNode
from haima.engines.contract.agent_role import display_agent_name
from haima.engines.contract.evidence import EvidenceRecord
from haima.engines.contract.research_graph_state import SectionState
from haima.engines.contract.section_definitions import SECTION_DEFINITIONS
from haima.engines.insight_agent.state import InsightState




class SectionPreparationNode(ResearchNode):
    """初始化固定章节并为各章节选择、排序和截取证据"""

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        """生成固定章节状态及供摘要节点消费的章节证据列表"""
        agent_name = display_agent_name(self.context.role)
        logger.info(f"{agent_name} 开始初始化固定章节并为各章节选择、排序和截取证据。")

        records_by_id = state.get("records_by_id")
        section_record_ids = state.get("section_record_ids")
        rerank_scores = state.get("rerank_scores")
        sections:list[SectionState] = []
        section_evidence_records:list[list[EvidenceRecord]] = []

        for section_definition in SECTION_DEFINITIONS.values():
            sections.append(
                {
                    "section_key":section_definition.key,
                    "title":section_definition.title,
                }
            )
            section_evidence_records.append(
                _select_section_records(
                    section_definition.key,
                    records_by_id,
                    section_record_ids,
                    rerank_scores
                )[:20]
            )
        logger.info(f"{agent_name} 初始化固定章节并为各章节选择、排序和截取证据完成")

        return {
            "sections":sections,
            "section_evidence_records":section_evidence_records
        }

def _select_section_records(section_key:str,
                            records_by_id:Mapping[str,EvidenceRecord],
                            section_record_ids:Mapping[str,list[str]],
                            rerank_scores:Mapping[str,float]
                            ) -> list[EvidenceRecord]:
    """按章节键筛选证据并按统一重排分降序排列"""
    matched_records = [
        records_by_id[record_id]
        for record_id in section_record_ids.get(section_key,[])   # todo
    ]
    return sorted(
        matched_records,
        key=lambda record: rerank_scores.get(record.id),
        reverse=True
    )