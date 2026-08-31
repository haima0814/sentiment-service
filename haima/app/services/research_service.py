from haima.engines.common.task_manager import task_manager
from haima.engines.orchestrator.orchestrator import OrchestratorResearchAgent


class ResearchService:
    def __init__(self):
        self.orchestrator = OrchestratorResearchAgent()

    def research(self,query:str)->str:
        """
        开始进行舆论话题的研究
        :param query:
        :return:
        """
        # 1.创建研究任务
        research_task = task_manager.create_research_task(query)

        # 2.利用协调manager将任务转发出去
        self.orchestrator.dispatch_task(research_task.task_id,query)

        # 3.将研究任务的ID返回
        return research_task.task_id