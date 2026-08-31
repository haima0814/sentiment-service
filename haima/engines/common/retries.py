import asyncio
from dataclasses import dataclass
from functools import wraps

from loguru import logger


@dataclass(slots=True)
class RetryConfig:
    init_delay: float = 1.0
    max_delay: float = 60
    max_retry: int = 3
    backoff_factor: float = 2.0

    def _compute_retry_delay(self, attempt: int) -> float:
        """
        计算重试次数的延迟时间
        :param attempt:
        :return:
        """
        delay = min(self.max_delay, self.init_delay * self.backoff_factor ** attempt)
        return delay

    def _no_retryable(self, e: Exception) -> bool:
        """
        是否需要重试
        :param e:
        :return:
        """

        status_code = getattr(e, "status_code", None)
        if status_code is None:
            status_code = getattr(getattr(e, "response", None), "status_code", None)

        return isinstance(status_code, int) and 400 <= status_code < 500 and status_code != 429

    def get_retry_delay(self, func_name: str, e: Exception, attempt: int) -> float | None:
        """
        获取延迟
        :param fuc_name:
        :param e:
        :param attempt:
        :return:
        """
        # 1.需要重试不
        if self._no_retryable(e) or attempt >= self.max_retry - 1:
            return None

        # 2.获取延迟
        delay = self._compute_retry_delay(attempt)

        current_try = attempt + 1
        next_try = current_try + 1

        logger.warning(f"函数 {func_name} 第 {current_try} 次尝试失败: {exec}")

        logger.info(f"将在 {delay:.1f} 秒后进行第 {next_try} 次尝试...")

        # 返回时间
        return delay


retry_config = RetryConfig()


def with_retry(func):
    """
    装饰器，对目标方法进行重试
    :param func:
    :return:
    """
    if not asyncio.iscoroutinefunction(func):
        raise TypeError("重试器只能修饰异步函数")

    @wraps(func)  # 使func的名字能正常使用，不然变成wrapper
    async def wrapper(*args, **kwargs):
        """
        *args,**kwargs:目标方法的参数个数是任意的且传参的形式及支持位置传参也支持关键字传参
        职责：重试调用目标方法
        重试点：
        根据响应码来决定哪些响应码需要重试，哪些响应码不需要重试。400<=response_code<500【客户端出现异常的响应码】  429除外【限流】
        重试次数：3次
        重试间隔：指数退避机制(动态机制)
        :return:
        """
        for attempt in range(retry_config.max_retry):
            try:
                return await func(*args,**kwargs)
            except Exception as e:
                delay = retry_config.get_retry_delay(func_name=func.__name__, e=e, attempt=attempt)
                if delay is None:
                    raise ValueError(f"{func.__name__}不需要重试 异常原因：{str(e)}")
                await asyncio.sleep(delay)

    return wrapper