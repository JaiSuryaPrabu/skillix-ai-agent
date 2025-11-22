# this is the first phase for the student learning

from google.adk.agents import SequentialAgent
from agents.specialized_agents.context_gathering_agent import create_context_gathering_agent,create_compaction_agent
from agents.specialized_agents.planning_agent import create_planning_agent

def create_research_phase():
    return SequentialAgent(
        name="ResearchPhaseAgent",
        description="Raw research to compaction to planning agent",
        sub_agents=[
            create_context_gathering_agent(),
            create_compaction_agent(),
            create_planning_agent()
        ]
    )