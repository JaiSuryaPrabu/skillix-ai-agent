from google.adk.agents import Agent
from google.adk.tools import AgentTool
from agents.specialized_agents.teaching_agent import create_teaching_agent
from agents.specialized_agents.evaluating_agent import create_evaluation_agent
from agents.memory.session_state import EvaluationResult

teaching_agent = create_teaching_agent()
evaluation_agent = create_evaluation_agent()


def create_dynamic_teaching_orchestrator() -> Agent:
    return Agent(
        name="DynamicTeachingOrchestrator",
        model="gemini-2.5-flash-lite",
        description="Adaptive tutor that decides in real-time whether to teach, quiz, hint, or advance",
        instruction="""
You are an expert adaptive tutor teaching one specific milestone.

CURRENT OBJECTIVE:
{current_milestone_content}

YOUR STATE AWARENESS:
- Previous evaluation result: {latest_eval_result}

YOUR AVAILABLE TOOLS:
- Teach: Call `TeachingAgent` → gives a fresh explanation
- Quiz: Call `EvaluationAgent` → asks a deep question and scores answer

YOUR DYNAMIC STRATEGY (follow exactly):

IF this is the first turn OR student has not mastered it yet:
   → Always start by calling `TeachingAgent` to give a clear explanation
   → Then immediately call `EvaluationAgent` to test understanding

IF student just answered (you can see latest_eval_result):
   → IF score >= 85 and mastered == true:
         → Respond with: "MASTERED"
         → Do not call any more tools
   → ELIF score >= 70:
         → Give gentle positive feedback + one targeted hint
         → Then call `EvaluationAgent` again (one more chance)
   → ELSE (score < 70):
         → Give constructive feedback highlighting the main misconception
         → Then call `TeachingAgent` with a different explanation style
         → Then call `EvaluationAgent` again

NEVER loop forever. After 4 total interactions, if not mastered, say "Let's reinforce this later" and respond "MOVE_ON"

You control the flow. Be empathetic, precise, and adaptive.

When you respond with "MASTERED", the outer loop will advance.
When you respond with "MOVE_ON", it will skip to next milestone.
""",
        tools=[
            AgentTool(teaching_agent),
            AgentTool(evaluation_agent),
        ],
    )