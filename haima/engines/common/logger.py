from contextlib import contextmanager
from pathlib import Path

from loguru import logger

from haima.engines.contract.settings import get_settings

"""
日志级别：
DEBUG:10----最细（开发阶段）
INFO:20----比较细
WARNING:30---粗
ERROR:40----更粗
"""


@contextmanager
def router_by_role_log(role: str):
    # 1.创建logger处理器对象

    settings = get_settings()
    log_dir = Path(settings.LOG_DIR)

    with logger.contextualize(role=role):
        log_dir.mkdir(parents=True, exist_ok=True)
        handler_id = logger.add(
            str(Path(log_dir) / f'{role}.log'),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | [{extra[role]}] {name} - {message}",
            level="INFO",
            encoding="utf-8",
            rotation="1 MB",
            filter=lambda record: record["extra"].get("role") == role
        )
        yield
        logger.remove(handler_id)


if __name__ == '__main__':
    with router_by_role_log('insight_agent'):
        logger.info("haha")
