# the goal of the teaching agent is to explain concept and ask questions

from google.adk.agents import Agent

def get_teaching_loop_instruction(context) -> str:
    """
    Dynamically fetches the current milestone content from session state.
    """
    state = context.session.state
    content = state.get("current_milestone_content", "No specific milestone content loaded yet. Ask the user to wait.")
    
    return f"""
    You are a world-class teacher. Your job is to explain the CURRENT milestone in a clear, engaging way.
        
    Current milestone: {content}
        
    Write a detailed, friendly explanation (300-500 words) with examples.
    End with a deep, open-ended question that tests true understanding.
        
    DO NOT output anything else. This will be shown to the user by the orchestrator.
    """

def create_teaching_agent()->Agent:
    '''
    Creates a teaching agent that does :
    1. Access the learning plan and user's learning style
    2. Teaches the concept with the objective milestone
    '''
    return Agent(
        name="TeachingAgent",
        model="gemini-2.5-flash-lite",
        description="Teaching agent that explains the concepts and asks deep questions",
        instruction=get_teaching_loop_instruction,
        output_key="teaching_explanation",
    )