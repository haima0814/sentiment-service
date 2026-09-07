from typing import Any

from langgraph.graph import StateGraph,START,END

from haima.engines.common.report_generation import ReportGenerationNode
from haima.engines.common.report_persistence import ReportPersistenceNode
from haima.engines.common.research_graph_runtime import ResearchRunContext, SECTION_SUMMARY_LOOP_MAPPING, \
    route_after_section_summary

from haima.engines.media_agent.nodes.search_planning_node import SearchPlanningNode
from haima.engines.media_agent.nodes.section_search_node import SearchNode
from haima.engines.media_agent.nodes.section_summary_node import SectionSummaryNode
from haima.engines.media_agent.state import MediaState


def build_graph(ctx:ResearchRunContext)->Any:
    graph = StateGraph(MediaState) # type: ignore
    graph.add_node("plan_search",SearchPlanningNode(ctx))
    graph.add_node("search",SearchNode(ctx))
    graph.add_node("summarize_sections",SectionSummaryNode(ctx))
    graph.add_node("generate_agent_report",ReportGenerationNode(ctx))
    graph.add_node("persist_agent_report",ReportPersistenceNode(ctx))

    graph.add_edge(START,"plan_search")
    graph.add_edge("plan_search","search")
    graph.add_edge("search","summarize_sections")
    graph.add_conditional_edges(
        "summarize_sections",
        route_after_section_summary,
        SECTION_SUMMARY_LOOP_MAPPING
    )
    graph.add_edge("generate_agent_report",'persist_agent_report')
    graph.add_edge("persist_agent_report",END)
    return graph.compile()

