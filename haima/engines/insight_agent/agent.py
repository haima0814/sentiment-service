import asyncio

from haima.engines.common.llm import LLMClient
from haima.engines.common.research_graph_runtime import ResearchRunContext, invoke_research_graph
from haima.engines.contract.agent_role import AgentInfoRoleKey
from haima.engines.contract.settings import get_settings
from haima.engines.insight_agent.graph import build_insight_graph


async def insight_agent_invoker(role:AgentInfoRoleKey,
                                task_id:str,
                                query:str,
                                llm_client:LLMClient,
                                output_dir:str):
    """
    Insight角色Agent的入口
    :param role:
    :param task_id:
    :param query:
    :param llm_client:
    :param output_dir:
    :return:
    """
    # 驱动执行insight 采用LangGraph框架

    context = ResearchRunContext(
        task_id=task_id,
        query=query,
        role=role,
        llm_client=llm_client,
        output_dir=output_dir
    )
    await invoke_research_graph(build_insight_graph(context),query)



async def main_test():
    await insight_agent_invoker(
        role="insight_agent",
        task_id="1234_test",
        query="高考难不难",
        llm_client=LLMClient.from_role("insight_agent"),
        output_dir=get_settings().RUNTIME_DIR
    )



if __name__ == '__main__':
    asyncio.run(main_test())