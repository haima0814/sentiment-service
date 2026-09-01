import asyncio
from typing import Any, TypeVar

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from pydantic import BaseModel

from haima.engines.common.retries import with_retry
# from loguru import logger
from haima.engines.contract.agent_role import AgentInfoRoleKey, AGENT_ROLE_INFOS
from haima.engines.contract.settings import get_settings


T = TypeVar("T",bound=BaseModel)

class LLMClient:
    """
    定义LLM客户端及模型调用方式
    """

    def __init__(self,
                 model_name: str,
                 model_provider: str,
                 api_key: str,
                 base_url: str):
        self.model_name = model_name
        self.model_provider = model_provider
        self.api_key = api_key
        self.base_url = base_url

    @classmethod
    def from_role(cls, role: AgentInfoRoleKey) -> "LLMClient":
        """
        根据角色获取LLM客户端
        :param role:
        :return:
        """

        # 1.获取配置信息
        settings = get_settings()

        # 2.获取Agent的配置信息前缀
        config_prefix = AGENT_ROLE_INFOS[role].config_prefix

        # 3.创建LLMClient
        return cls(
            model_name=getattr(settings, f"{config_prefix}_MODEL_NAME"),
            model_provider=getattr(settings, f"{config_prefix}_MODEL_PROVIDER"),
            api_key=getattr(settings, f"{config_prefix}_API_KEY"),
            base_url=getattr(settings, f"{config_prefix}_BASE_URL")
        )

    @with_retry
    async def generate_text(self,
                            system_prompt: str,
                            user_prompt: str
                            ) -> str:
        """
        调用LLMClient返回文本内容，选择异步调用，流式输出
        原因：用流式的方式使的超长文本超时连接更加稳定安全
        :param system_prompt:
        :param user_prompt:
        :return:
        """
        # 1.构建消息内容
        message_context = self._build_message_context(system_prompt, user_prompt)

        # 2.定义模型实例
        chat_model = self.init_model_object()

        # 3.调用模型
        final_chunks = []
        try:
            async for chunk in chat_model.astream(message_context):
                if text:=chunk.content:
                    final_chunks.append(text)
                    # logger.info(f"切片内容: {chunk}")
        except Exception as e:
            raise ValueError(f"{self.model_name}调用失败，原因{str(e)}")

        return ''.join(final_chunks)


    @with_retry
    async def generate_object(self,
                            system_prompt: str,
                            user_prompt: str,
                            structed_object: type[T]
                            ) -> T:
        """
        职责：调用LLMClient返回结构化对象(BaseModel)
        如何确保LLM一定能输出结构化对象。
        json_model(json_object)--保证输出JSON结构，提示词要求JSON内部字段结构。
        json_schema---物理层面保证输出的一定是遵循JSON_SCHEMA.无需在提示词中额外说明组（模型不支持）
        Function_calling：早期(保留下来)：自定义函数_最通用的
        Tool_calling:支持集成三方的工具函数以及并行执行,Agent推理速度响应都会更快
        :return:
        """
        # 1.构建消息内容
        message_context = self._build_message_context(system_prompt, user_prompt)

        # 2.定义模型实例
        chat_model = self.init_model_object(is_structured=True)

        structured_output = chat_model.with_structured_output(structed_object,method='json_schema')

        # 3.调用模型
        try:
            llm_response = await structured_output.ainvoke(message_context)
        except Exception as e:
            raise ValueError(f"{self.model_name}调用失败，原因{str(e)}")

        if llm_response is None:
            raise ValueError(f"{self.model_name}输出结构化对象为None")

        return llm_response



    def _build_message_context(self,
                               system_prompt: str,
                               user_prompt: str) -> list[BaseMessage]:
       """
       将系统提示词和用户提示词封装成LangChain统一的消息类型
       :param system_prompt:
       :param user_prompt:
       :return:
       """
       return [
           SystemMessage(content=system_prompt),
           HumanMessage(content=user_prompt)
       ]

    def init_model_object(self, is_structured:bool = False)->BaseChatModel:

        # kimi-k3模型思考模型要禁用掉
        model_name = self.model_name.lower()
        kwargs: dict[str, Any] = {}
        if is_structured and ('kimi' in model_name or 'moonshot' in model_name ):
            kwargs["extra_body"] = {
                "thinking":{
                    "type": "disabled"
                }
            }
        return init_chat_model(
            model_provider=self.model_provider,
            model=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url,
            **kwargs
        )


if __name__ == '__main__':
    llm = LLMClient.from_role("insight_agent")
    res = asyncio.run(llm.generate_text("你是一个助手", "你叫什么名字"))
    print(res)

