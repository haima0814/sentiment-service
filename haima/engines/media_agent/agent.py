import asyncio

from scipy.stats import median_test

from haima.engines.common.llm import LLMClient
from haima.engines.common.report import get_report_dir
from haima.engines.common.research_graph_runtime import ResearchRunContext, invoke_research_graph
from haima.engines.contract.agent_role import AgentInfoRoleKey
from haima.engines.media_agent.graph import build_graph


async def media_agent_invoker(role: AgentInfoRoleKey,
                              task_id: str,
                              query: str,
                              llm_client: LLMClient,
                              output_dir: str):
    """
    Media角色Agent的入口
    :param role:
    :param task_id:
    :param query:
    :param llm_client:
    :param output_dir:
    :return:
    """
    # 驱动执行media用 Langgraph编排的工作流
    context = ResearchRunContext(
        task_id=task_id,
        query=query,
        role=role,
        llm_client=llm_client,
        output_dir=output_dir
    )
    await invoke_research_graph(build_graph(context),query=query)


async def mian_test():
    await media_agent_invoker(
        role="media_agent",
        task_id="1234_test",
        query="高考",
        llm_client=LLMClient.from_role("media_agent"),
        output_dir=get_report_dir("1234_test", "media_agent")
    )

if __name__ == '__main__':
    asyncio.run(mian_test())