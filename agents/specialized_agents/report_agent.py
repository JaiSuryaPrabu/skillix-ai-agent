# Code for the final report agent
from typing import List
from pydantic import BaseModel, Field
from google.adk.agents import Agent

class LearningJourneyReport(BaseModel):
    '''
    Complete final report of the student's learning journey
    '''
    topic: str = Field(..., description="The main topic studied")
    total_milestones: int = Field(..., description="Total steps in the plan")
    completed_milestones: int = Field(..., description="How many steps were fully mastered")
    overall_mastery_score: float = Field(..., description="Average score across completed steps")
    strongest_areas: List[str] = Field(..., description="Top 2-3 concepts the student excelled at")
    areas_for_improvement: List[str] = Field(..., description="Key misconceptions or weak areas")
    key_takeaways: List[str] = Field(..., description="3-5 most important insights from the journey")
    recommendation: str = Field(..., description="Next steps or deeper topics to explore")
    final_grade: str = Field(..., description="A+, A, B+, etc. — motivational grade")


def create_final_report_agent() -> Agent:
    '''
    FinalReportAgent creates a insightful summary of the entire learning session.
    Reads all prior state (learning_plan, evaluation results) and generates structured + human-readable report.
    '''
    return Agent(
        name="FinalReportAgent",
        model="gemini-2.5-flash-lite",
        
        description="Expert learning analyst that creates professional, insightful final reports on a student's adaptive learning journey.",
        
        instruction="""
You are FinalReportAgent — a world-class learning experience designer and analyst.

You have access to:
- The full learning_plan (all milestones)
- evaluation_result from each completed step
- current_step_index (how far the student progressed)
- All scores, feedback, and misconceptions

Your mission:
Create a warm, encouraging, and deeply insightful final report.

Include:
1. Clear summary of progress (X out of Y milestones mastered)
2. Overall mastery score (average of all evaluation scores)
3. Strongest areas (where student scored 90+)
4. Areas for improvement (recurring misconceptions)
5. 3-5 key takeaways the student truly internalized
6. Personalized recommendation for next steps

Tone: Professional, warm, encouraging, and precise.
End with a motivational final grade (A+, A, B+, etc.).

Output must be valid JSON matching the LearningJourneyReport schema.
""",
        output_schema=LearningJourneyReport,
        output_key="final_learning_report",
    )