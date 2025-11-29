# Action phase connects the teaching agent and evaluation agent as one

from typing import Dict, Any

from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.tools import FunctionTool  # Use FunctionTool for exit_loop (as in sample)

from agents.specialized_agents.evaluating_agent import create_evaluation_agent
from agents.specialized_agents.teaching_agent import create_teaching_agent


def should_continue_loop(
    evaluation_result: Dict[str, Any],
    current_step_index: int,
    total_steps: int
) -> Dict[str, str]:
    '''
    Determines whether the loop should continue or not (helper for decision agent).
    
    Args:
        - evaluation_result: Dict[str,Any] - the result of the evaluation agent
        - current_step_index: int - current milestone number
        - total_steps: int - total number of milestones

    Returns:
        {"status": "continue"} or {"status":"stop"}
    '''
    if current_step_index >= total_steps:
        return {"status": "stop", "reason": "All steps completed"}
    
    mastered = evaluation_result.get("mastered", False)
    score = evaluation_result.get("score", 0)

    if mastered and score >= 80:
        return {"status": "stop", "reason": f"Step {current_step_index + 1} mastered (score: {score})"}
    else:
        return {"status": "continue", "reason": f"Step {current_step_index + 1} needs reinforcement (score: {score})"}

def exit_loop():
    """Call this function ONLY when the evaluation is mastered (score >=80), indicating the milestone is complete and no more teaching is needed."""
    return {"status": "mastered", "message": "Milestone mastered. Exiting teaching loop."}

def create_loop_decision_agent() -> Agent:
    '''
    Agent for deciding whether to continue the loop or not.
    Reads {latest_eval_result}, calls should_continue_loop, and calls exit_loop() ONLY if "stop" (mastered).
    Outputs ONLY "CONTINUE" otherwise (signal for next iteration, like sample's rewrite).
    '''
    return Agent(
        name="LoopDecisionAgent",
        model="gemini-2.5-flash-lite",
        description="Decides whether to continue teaching loop or advance to next step",
        instruction="""You are a loop decision agent and you are in control of the loop. Your task is to evaluate the {latest_eval_result} from the EvaluationAgent, current step index, and total number of steps in the milestone. Call should_continue_loop with the right parameters and check the 'status'.

- IF the status is 'stop' (mastered), you MUST call the `exit_loop` function and nothing else (this exits the loop).
- OTHERWISE, respond with the exact phrase: "CONTINUE" (to signal another teaching iteration).

Output ONLY the exact word "CONTINUE" if not exiting. Nothing else.""",
        tools=[
            should_continue_loop,
            FunctionTool(exit_loop)
        ],
        output_key="loop_decision"
    )

def create_teaching_evaluation_cycle() -> SequentialAgent:
    return SequentialAgent(
        name="TeachingEvaluationCycle",
        description="Teach -> Evaluate -> Decide to continue or stop",
        sub_agents=[
            create_teaching_agent(),
            create_evaluation_agent(),
            create_loop_decision_agent(),
        ]
    )

def create_action_phase_agent() -> LoopAgent:
    '''
    Uses LoopAgent for evaluation loop (as in sample's story_refinement_loop).
    Iterates the cycle until exit_loop() is called (dynamic termination) or max_iterations.
    Final state (latest_eval_result from last eval) persists via sub-agent output_key.
    '''
    return LoopAgent(
        name="TeachingLoopAgent",
        description="Teaches the CURRENT milestone and evaluates understanding until student masters the current milestone",
        sub_agents=[create_teaching_evaluation_cycle()],
        max_iterations=5
    )