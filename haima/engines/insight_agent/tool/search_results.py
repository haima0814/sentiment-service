from dataclasses import dataclass, field

from haima.engines.contract.evidence import EvidenceDocument


@dataclass(slots=True)
class SearchResult:
    """mysql召回结果"""

    retrieval_channel: str
    retrieval_results: list[EvidenceDocument] = field(default_factory=list)


@dataclass(slots=True)
class SearchHit:
    """Milvus包含检索元数据的单条"""

    retrieval_score: float
    retrieval_channel: str
    retrieval_document: EvidenceDocument
