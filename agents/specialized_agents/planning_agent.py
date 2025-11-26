# the goal of the planning agent is to create syllabus and store it in memory

from google.adk.agents import Agent
from agents.memory.session_state import LearningPlan

def create_planning_agent() -> Agent:
    '''
    Creates a specialized planning agent that :
    1. Thinks about the user's preference
    2. Creates the syllabus based on personalized roadmap
    3. Saves the state in learning_plan
    '''
    return Agent(
        name="PlanningAgent",
        model="gemini-2.5-flash-lite",
        description="Expert curriculum designer that creates adaptive, personalized learning roadmaps",
        instruction="""You are a planning agent - a personalized curriculum designer for deep topics. You have access to the high-quality knowledge base in {context_knowledge_base}. Your task is to think and analyze the topic and the curated sources and infer the user's current level based on the context. Based on the teaching style come up with a learning roadmpa with 5-10 milestones each milestone should have clear objective. Do not add other than milestone.""",
        output_schema=LearningPlan,
        output_key="learning_plan"
    )