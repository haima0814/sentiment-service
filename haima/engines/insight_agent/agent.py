from haima.engines.common.llm import LLMClient
from haima.engines.common.research_graph_runtime import ResearchRunContext, invoke_research_graph
from haima.engines.contract.agent_role import AgentInfoRoleKey
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
    # 驱动执行insight 采用LangGraph框架·

    context = ResearchRunContext(
        task_id=task_id,
        role=role,
        llm_client=llm_client,
        output_dir=output_dir
    )
    await invoke_research_graph(build_insight_graph(context),query)