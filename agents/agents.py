from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool,google_search,load_memory
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService

MODEL_NAME = "gemini-2.5-flash-lite"
MODEL = Gemini(model=MODEL_NAME)

# ADK's built-in Memory Service. Create Session Service
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

# Content Search Agent: Its job is to use the google_search tool and present content.
search_agent = LlmAgent(
    name="SearchAgent",
    description="Search Agent will search the internet and provide result based on the request",
    model=MODEL,
    instruction="""You are a Search Agent and your only goal is to search the topic mentioned and provide curated result as the response""",
    tools=[google_search]
)

search_agent_tool = AgentTool(search_agent)

# planning agent - Builds personalized learning syllabus based on user's topic.
planning_agent = LlmAgent(
    name="PlanningAgent",
    description="Planning agent will plan the syllabus based on the user's topic",
    model=MODEL,
    instruction="""You are a planning agent and your main goal is to create the syllabus. You can use SearchAgent as a tool to search the up-to-date information on the topic mentioned and come up with a structured list of syllabus""",
    tools=[search_agent_tool,load_memory]
)

planning_agent_tool = AgentTool(planning_agent)

# teaching agent - provides the explanation on a user's topic
teaching_agent = LlmAgent(
    name="TeachingAgent",
    description="Teaching Agent will provide the explanation or clarify the doubts in a particular topic",
    model=MODEL,
    instruction="""You are a teaching agent and your main goal is to explain a topic mentioned or clarify the doubt asked. You can use SearchAgent as a tool to search the up-to-date information on the topic asked and provide clear explanation with examples. Your teaching style should make the user grasp concept and make the user to think not just spoon feed the entire content""",
    tools=[search_agent_tool]
)

teaching_agent_tool = AgentTool(teaching_agent)

# evaluation agent - assess the user's understanding on a topic
evaluation_agent = LlmAgent(
    name="EvaluationAgent",
    description="Evaluation agent is to assess the understanding of the user's learning on the topic",
    model=MODEL,
    instruction="""You are a evaluation agent and your main goal is to perform a structured assessment of user understanding on the topic. You can use `google_search` to find the facts and compare with the user's explanation on the topic and assess with facts and tell the strengths and weakness of the user's understanding"""
)

evaluation_agent_tool = AgentTool(evaluation_agent)

async def auto_save_to_memory(callback_context):
    """Automatically save session state to memory after each orchestrator agent turn"""
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )

#Orchestrator agent - Manages the flow of tasks between other agents
root_orchestrator = LlmAgent(
    name="LearningOrchestrator",
    description="The orchestrator agent that delegates the tasks and managees the learning journey state.",
    model=MODEL,
    instruction="""You are the main learning orchestrator. Your goal is to guide the user through a multi-step learning journey.
    1. Ask the user for the topic and expertise level in the topic
    2. Use the PlanningAgent to get the syllabus
    3. Use the TeachingAgent to get the teaching concept of the topic or if the user has a doubt on the topic
    4. Use the EvaluationAgent to check the user's understanding on the topic
    5. At the end generate a detailed learning report using accumulated data in the memory

    Always use PlanningAgent or TeachingAgent or EvaluationAgent's response into a meaningful structured information to the user. Always think about the previous conversations with the user and current user's request and then use the specialized agents and provide the response to the user as the specialized agent responded and do not share your own thoughts always use the specialized agent's response for the user's request.
    """,
    tools=[planning_agent_tool,teaching_agent_tool,evaluation_agent_tool,load_memory],
    after_agent_callback=auto_save_to_memory,
)

def get_runner():
    return Runner(
        agent=root_orchestrator,
        app_name="SkillixAI",
        session_service=session_service,
        memory_service=memory_service
    )