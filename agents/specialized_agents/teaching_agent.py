# the goal of the teaching agent is to explain concept and ask questions

from google.adk.agents import Agent

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
        instruction="""You are a specialized teaching agnet and you access to {learning_plan} and give a clear explanation for the current milestone and always end with a deep, open ended question that forces the student to think and demonstrate the understanding. If the score is very less then provide examples and insights to help the student to grasp the content. Never move to next step unless the score is reasonable."""
    )