from collections.abc import Callable
from typing import Awaitable

from loguru import logger

from haima.engines.common.llm import LLMClient
from haima.engines.common.logger import router_by_role_log
from haima.engines.common.report import get_report_dir
from haima.engines.common.task_manager import task_manager
from haima.engines.contract.agent_role import AgentInfoRoleKey
from haima.engines.insight.agent import insight_agent_invoker
from haima.engines.media.agent import media_agent_invoker

AGENT_INVOKER = Callable[[AgentInfoRoleKey, str, str, LLMClient, str], Awaitable[None]]


class OrchestratorResearchAgent:

    def __init__(self):
        self.agent_invoker: dict[AgentInfoRoleKey, AGENT_INVOKER] = {
            "insight": insight_agent_invoker,
            "media": media_agent_invoker
        }

    def dispatch_task(self,
                      task_id: str,
                      query: str):
        """
        将研究任务转发给研究角色的Agent处理.
        启动两个角色Agent执行的异步任务
        :param task_id:
        :param query:
        :return:
        """
        for agent_role in self.agent_invoker.keys():
            task_manager.submit_task(self.execute_research_task(task_id, query, agent_role))

    async def execute_research_task(self,
                                    task_id: str,
                                    query: str,
                                    role: AgentInfoRoleKey):
        with router_by_role_log(role):
            try:
                # 1.获取两个角色的llm客户端
                llm_client = LLMClient.from_role(role)

                # 2.得到md文档的目录
                output_dir = get_report_dir(task_id, role)

                # 3.执行两个Agent
                await self.agent_invoker[role](
                    role,
                    task_id,
                    query,
                    llm_client,
                    output_dir
                )
            except Exception as e:
                logger.error(
                    f"{role} 研究智能体执行期间出现了异常: {e}"
                )
                return
