import asyncio
from datetime import datetime, timedelta

import jieba.analyse

from haima.engines.contract.evidence import EvidenceRecord, EvidenceDocument, RetrievalMeta
from haima.engines.contract.settings import get_settings
from haima.engines.insight_agent.tool.db.repository import DatabaseSearchRepository
from haima.engines.insight_agent.tool.search_results import SearchHit, SearchResult
from haima.engines.insight_agent.tool.vector.repository import VectorSearchRepository


class RetrivalService:

    def __init__(self):
        self.db_repository = DatabaseSearchRepository()
        self.vectory_repository = VectorSearchRepository() if get_settings().INSIGHT_VECTOR_ENABLED else None

    async def retrival_evidence(self, query: str) -> list[EvidenceRecord]:
        """
        职责：查询两个通道结果都完成，返回两个通道结果
        :param query:
        :return:
        """

        db_evidence, vector_evidence = await  asyncio.gather(
            self._retrival_db_evidence(query), self._retrival_vector_evidence(query)
        )

        return [*db_evidence, *vector_evidence]

    async def _retrival_vector_evidence(self, query: str) -> list[EvidenceRecord]:
        """
        职责： 从向量数据库中查询检索到的结果
        :param query:
        :return:
        """
        # 1.判断是否启用了向量检索
        if self.vectory_repository is None:
            return []

        # 2.检索
        search_hits: list[SearchHit] = await asyncio.to_thread(self.vectory_repository.vector_call,
                                                               query, 50, build_filter_expr())
        # 3. 结果处理
        return [map_document_to_evidence(
            document=hit.retrieval_document,
            matched_queries=query,
            retrival_channel=hit.retrieval_channel,
            retrival_score=hit.retrieval_score
        )
            for hit in search_hits
        ]

    async def _retrival_db_evidence(self, query: str) -> list[EvidenceRecord]:
        """
        职责：从MySQL数据库中查询检索到的结果
        只要记录来源于db通道，记录的得分固定是1.0（0.5）
        :param query:
        :return:
        """
        # 1.对查询问题分词
        terms = extract_terms(query)

        # 2.分别用分词后的词进行模糊查询
        results:list[SearchResult] = await asyncio.gather(
          *(self.db_repository.db_call(term,limit=20)  for term in terms)
        )

        # 3.处理结果
        return [
            map_document_to_evidence(
                document=document,
                matched_queries=term,
                retrival_channel=search_result.retrieval_channel,
                retrival_score=0.5
            )
            for term,search_result in zip(terms,results)
            for document in search_result.retrieval_results
        ]



def build_filter_expr() -> str:
    days = get_settings().INSIGHT_VECTOR_FILTER_DAYS

    start_time = int((datetime.now() - timedelta(days=days)).timestamp())

    return f"published_at>={start_time}"


def map_document_to_evidence(document: EvidenceDocument,
                             matched_queries: str,
                             retrival_channel: str,
                             retrival_score: float
                             ) -> EvidenceRecord:
    return EvidenceRecord(
        document=document,
        retrieval=RetrievalMeta(
            matched_queries=[matched_queries],
            channel_scores={
                retrival_channel: retrival_score
            }
        )
    )


def extract_terms(query: str) -> list[str]:
    """
    1. 简单
    2. 指定分词的数量
    3. 去掉无用的词性：的、了、啊
    分词的数量：需要根据压测给到（2--6-8-->10）
    :param query:
    :return:
    """
    final_terms = [query]
    for term in jieba.analyse.extract_tags(query, 3):
        if 2 <= len(term) <= 4 and term not in final_terms:
            final_terms.append(term)
    return final_terms


async def main_test():
    retrival_service = RetrivalService()

    results = await  retrival_service.retrival_evidence(query="高考成绩查询")

    print(len(results))

if __name__ == '__main__':
    asyncio.run(main_test())