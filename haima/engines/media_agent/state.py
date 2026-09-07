from haima.engines.contract.evidence import EvidenceRecord
from haima.engines.contract.research_graph_state import ResearchGraphState, SectionState
from haima.engines.media_agent.web_search.provider import SearchTool


class MediaSectionState(SectionState):
    search_tool:SearchTool
    search_keywords:list[str]




class MediaState(ResearchGraphState[MediaSectionState],total=False):
    section_evidence_records:list[list[EvidenceRecord]]
    section_queries:list[str]