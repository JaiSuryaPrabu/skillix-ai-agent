# the goal of the evaluation agent is to score the students and response and store the information of what are the wrong answers

from typing import List
from pydantic import BaseModel,Field

from google.adk.agents import Agent

class EvaluationResult(BaseModel):
    '''
    Structured result from evaluation - automatically saved via output_key
    '''
    score:int = Field(...,ge=0,le=100,description="Understanding score from 0 to 100")
    misconceptions: List[str] = Field(default_factory=list,description="List of specific misconceptions")
    feedback:str = Field(...,description="Clear, constructive feedback to student")
    mastered:bool = Field(...,description="True if score >= 80")

def create_evaluation_agent() -> Agent:
    '''
    Creates the evaluation agent that :
    1. Reads the current learning milestone and student's answer
    2. Scores understanding strictly from 0 to 100
    3. Detects the misconception
    4. Outputs structured EvaluationResult 
    '''
    return Agent(
        name="EvaluationAgent",
        model="gemini-2.5-flash-lite",
        description="Strict but fair technology examiner that scores answers and detects deep misconceptions",
        instruction="""You are evaluation agent and your task to get the current learning objective and student's answer and deeply evaluate understanding of the core concept and score from the scale of 0 to 100 based on few rules like 90 to 100 for exceptional depth, 80 to 90 for solid grasp, 70-80 parital but flawed, 60 - 70 okay but needed improvements and less than 60 is a major misconceptions and based on the scoring identify the precise misconceptions and write clearn, constructive feedback and set mastered as True only when score is greater than 80. Output must be valid type matching the EvaluationResult schema""",
        output_key="evaluation_result",
        output_schema=EvaluationResult
    )