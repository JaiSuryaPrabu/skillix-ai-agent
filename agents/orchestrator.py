# the main agent that delegates tasks to specialized agents

from google.adk.agents import Agent
from google.adk.tools import AgentTool

from .specialized_agents.research_phase import create_research_phase
from .specialized_agents.action_phase import create_action_phase_agent_v2
from .specialized_agents.report_agent import create_final_report_agent

def create_orchestrator_agent() -> Agent:
    '''
    This is the deep agent level orchestrator that uses all the specialzied agents as Tools and decides the full flow dynamically
    '''
    return Agent(
        name="RootOrchestrator",
        model="gemini-2.5-flash-lite",
        description="Root orchestrator that manages the entire learning system for the student",
        instruction="""You are the Root Orchestrator Agent and you have three phases available as tools :
        1. ResearchPhaseAgent - Gathers knowledge and creates a personalized learning plan
        2. TeachingLoopAgent - Runs teaching with evaluation until the student masters the material
        3. FinalReportAgent - Creates a final report for the student's overall performance

        Critical workflow rules - you must follow this order:
        1. Alway start by calling ResearchPhaseAgent for any new topic
        2. Once the learning_plan exists, call TeachingLoopAgent
        3. When the teaching loop finishes, call FinalReportAgent
        4. After the final report is generated, end the session with warm congratulations

        You can see the current state (learning_plan,evaluation results, current_step_index) at any time. Never skip steps. Never generate reports on your own and never teach without a plan. Be encouraging, professional and precise.
        """,
        tools = [
            AgentTool(create_research_phase()),
            AgentTool(create_action_phase_agent_v2()),
            AgentTool(create_final_report_agent())
        ]
    )