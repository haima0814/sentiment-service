import json
from typing import Any

from langchain_core.prompts import PromptTemplate
from loguru import logger

from haima.engines.common.research_graph_runtime import ResearchNode
from haima.engines.contract.agent_role import display_agent_name
from haima.engines.contract.section_definitions import get_section_definitions_for_role, SECTION_DEFINITIONS
from haima.engines.media_agent.search_plan import MediaSearchPlanOutput
from haima.engines.media_agent.state import MediaState, MediaSectionState
from haima.engines.media_agent.web_search.search_results import SEARCH_TOOL_DESCRIPTIONS
from haima.engines.prompts.media import MEDIA_SEARCH_PLAN_USER_PROMPT, MEDIA_SEARCH_PLAN_SYSTEM_PROMPT


class SearchPlanningNode(ResearchNode):
    """为固定 Media 章节生成搜索工具与关键词"""

    async def __call__(self,state:MediaState)->dict[str,Any]:
        """调用 LLM 生成搜索策略，并与固定章节定义合并为运行状态"""
        agent_name = display_agent_name(self.context.role)
        logger.info(f"【{agent_name}】开始执行公域信息搜索")
        planned = await self._generate_search_plan(self.context.query)

        sections:list[MediaSectionState] = [
            MediaSectionState(
                section_key=section_definition.key,
                title=section_definition.title,
                search_tool=planed_section.search_tool,
                search_keywords=[keyword.strip() for keyword in planed_section.search_keywords]
            )
            for section_definition,planed_section in zip(
                SECTION_DEFINITIONS.values(),planned.sections
            )
        ]

        logger.info(f"【{agent_name}】执行公域信息搜索完成")
        return {"sections":sections}


    async def _generate_search_plan(self,
                                    research_topic:str)->MediaSearchPlanOutput:

        search_tools = [
            {"name":tool,"description":description}
            for tool,description in SEARCH_TOOL_DESCRIPTIONS.items()
        ]

        prompt = PromptTemplate.from_template(MEDIA_SEARCH_PLAN_USER_PROMPT).format(
            research_topic=research_topic,
            section_contexts=json.dumps(
                get_section_definitions_for_role(self.context.role),
                ensure_ascii=False,
                indent=2,
            ),
            search_tools=json.dumps(
                search_tools,
                ensure_ascii=False,
                indent=2
            )
        )


        return await self.context.llm_client.generate_object(
            MEDIA_SEARCH_PLAN_SYSTEM_PROMPT,
            prompt,
            MediaSearchPlanOutput
        )