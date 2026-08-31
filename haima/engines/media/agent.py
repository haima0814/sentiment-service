from haima.engines.common.llm import LLMClient
from haima.engines.contract.agent_role import AgentInfoRoleKey


async def media_agent_invoker(role:AgentInfoRoleKey,
                                task_id:str,
                                query:str,
                                llm_client:LLMClient,
                                output_dir:str):
    """
    Media角色Agent的入口
    :param role:
    :param task_id:
    :param query:
    :param llm_client:
    :param output_dir:
    :return:
    """
    pass