from dataclasses import dataclass
from typing import Literal

AgentInfoRoleKey = Literal["insight_agent", "media_agent", "host", "report"]

@dataclass(slots=True)
class AgentRoleInfo:
    """
    不同角色Agent信息
    """
    config_prefix:str
    display_name:str

AGENT_ROLE_INFOS:dict[AgentInfoRoleKey,AgentRoleInfo] = {
    "insight_agent":AgentRoleInfo(display_name="私域检索专家",config_prefix="INSIGHT_AGENT"),
    "media_agent": AgentRoleInfo(display_name="公域检索专家", config_prefix="MEDIA_AGENT"),
    "host": AgentRoleInfo(display_name="主持人研判专家", config_prefix="HOST_AGENT"),
    "report": AgentRoleInfo(display_name="综合报告引擎", config_prefix="REPORT_ENGINE")
}


def display_agent_name(role_key:AgentInfoRoleKey)->str:
    return AGENT_ROLE_INFOS[role_key].display_name