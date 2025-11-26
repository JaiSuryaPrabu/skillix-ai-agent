# Code for the final report agent
from typing import List
from pydantic import BaseModel, Field
from google.adk.agents import Agent

class LearningJourneyReport(BaseModel):
    topic: str
    total_milestones: int
    mastered_milestones_count: int
    mastered_milestone_list: List[str] = Field(..., description="Exact objectives mastered")
    overall_mastery_score: float
    strongest_areas: List[str]
    areas_for_improvement: List[str]
    key_takeaways: List[str]
    recommendation: str
    final_grade: str
    total_attempts: int = Field(..., description="Total teaching loops run (insight into effort)")


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

- Topic: {topic}
- Full learning_plan with {total_milestones} milestones
- evaluation_history: a list of EVERY mastered milestone with real scores, feedback, and misconceptions
- completed_milestones: list of milestone objectives the student actually mastered
- current_step_index: how far they got

YOUR MISSION: Write a warm, honest, and deeply insightful final report using ONLY real data.

REQUIRED SECTIONS:
1. Progress Summary
   - "You mastered X out of Y milestones"
   - List the mastered milestone objectives clearly

2. Overall Mastery Score
   - Calculate: average of all scores in evaluation_history
   - Show the number

3. Strongest Areas
   - Look for milestones with score ≥ 90
   - Name 2-3 specific concepts

4. Areas for Improvement
   - Find recurring themes in feedback/misconceptions across history
   - Be specific but encouraging

5. Key Takeaways (3-5 bullet points)
   - What the student truly internalized (based on high scores + clean understanding)

6. Personalized Next Steps
   - Recommend deeper topics or review areas

7. Final Motivational Grade
   - A+, A, B+, etc. based on % mastered and average score

Tone: Warm, proud, precise, human. Never generic.

Use only the real evaluation_history — do not invent progress.
""",
        output_schema=LearningJourneyReport,
        output_key="final_report",
    )