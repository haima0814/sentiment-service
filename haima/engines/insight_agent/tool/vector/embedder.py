from functools import cached_property
from typing import Iterable

from FlagEmbedding import BGEM3FlagModel

from haima.engines.contract.settings import get_settings


def _normalize_sparse_vector(sparse_vector:dict)->dict[int,float]:
    """将稀疏向量字典的键和值分别转换为整数 Token ID 与浮点数权重"""
    return {
        int(token_id):float(weight)
        for token_id, weight in sparse_vector.items()
    }


class VectorEmbedder:
    """封装BGEM3模型"""

    @cached_property
    def model(self) -> BGEM3FlagModel:
        """按配置蹲星创建BGE-M3模型"""
        settings = get_settings()
        device = settings.INSIGHT_EMBEDDING_DEVICE

        return BGEM3FlagModel(
            settings.INSIGHT_EMBEDDING_MODEL,
            use_fp16="cpu" not in device.lower(),
            devices=device
        )

    def encode(self, texts: Iterable[str]
               ) -> list[tuple[list[float], dict[int, float]]]:
        """生成稠密稀疏向量"""
        text_items = list(texts)
        model_output = self.model.encode(
            text_items,
            return_dense=True,
            return_sparse=True
        )

        return [
            (dense.tolist(),_normalize_sparse_vector(sparse))
            for dense,sparse in zip(
                model_output["dense_vecs"],model_output["lexical_weights"]
            )
        ]


if __name__ == '__main__':
    vector = VectorEmbedder()
    vector.encode(texts=["我是你爹"])
    print('****')