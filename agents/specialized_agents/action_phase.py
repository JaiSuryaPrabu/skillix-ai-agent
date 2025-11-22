# Action phase connects the teaching agent and evaluation agent as one

from google.adk.agents import Agent,ParallelAgent,LoopAgent,SequentialAgent
from agents.specialized_agents.teaching_agent import create_teaching_agent
from agents.specialized_agents.evaluating_agent import create_evaluation_agent

from typing import Dict, Any

def should_continue_loop(
        evaluation_result: Dict[str,Any],
        current_step_index: int,
        total_steps: int
) -> Dict[str,str]:
    '''
    Determines whether the loop should continue or not
    
    Args:
        - evaluation_result : Dict[str,Any] - the result of the evaluation agent
        - current_step_index : int - current milestone number
        - total_steps : int - total number of milestones

    Returns:
        {"status": "continue"} or {"status":"stop"}
    '''
    if current_step_index >= total_steps:
        return {"status":"stop","reason":"All steps completed"}
    
    score = evaluation_result.get("score",0)
    mastered = evaluation_result.get("mastered",score>=80)

    if mastered:
        return {"status": "stop", "reason": f"Step {current_step_index + 1} mastered (score: {score})"}
    else:
        return {"status": "continue", "reason": f"Step {current_step_index + 1} needs reinforcement (score: {score})"}
    
def create_loop_decision_agent() -> Agent:
    '''
    Agent for deciding whether to continue the loop or not
    '''
    return Agent(
        name="LoopDecisionAgent",
        model="gemini-2.5-flash-lite",
        description="Decides whether to continue teaching loop or advance to next step",
        instruction="""You are a loop decision agent and you are in control of the loop. Your task is to evaluate the {evaluation_result} from the EvaluationAgent and current step index of the milestone and total number of steps in the milestone and call should_continue_loop with the right set of parameters and check the 'status' to decide either to continue that loop (return 'CONTINUE') or stop the loop (return 'STOP'). Output ONLY one of these exact words. Nothing else""",
        tools=[should_continue_loop],
        output_key="loop_decision"
    )

def create_action_phase_agent_v1() -> LoopAgent:
    '''
    Creates the looping agent
    '''

    full_iteration_agent = SequentialAgent(
        name="TeachingEvaluationCycle",
        description="Single sequential pass of Teaching agent to Evaluation agent to Decision agent",
        sub_agents=[
            create_teaching_agent(),
            create_evaluation_agent(),
            create_loop_decision_agent(),
        ]
    )

    return LoopAgent(
        name="TeachingLoopAgent",
        description="Loop of the teaching phase",
        sub_agents=[full_iteration_agent],
        max_iterations=10
    )

def create_parallel_teach_eval_agent() -> ParallelAgent:
    '''
    Runs the teaching agent and evaluation agent in parallel when possible.
    This speeds up the process and doesn't depends on each other
    '''
    return ParallelAgent(
        name="ParallelTeachAndEvaluateAgent",
        sub_agents=[
            create_teaching_agent(),
            create_evaluation_agent(),
        ]
    )

def create_action_phase_agent_v2() -> LoopAgent:
    '''
    Uses parallel agent with evaluation loop
    '''
    parallel_step = create_parallel_teach_eval_agent()

    decision_step = create_loop_decision_agent()

    full_iteration = SequentialAgent(
        name="OneTeachingIteration",
        sub_agents=[
            parallel_step,
            decision_step
        ]
    )

    return LoopAgent(
        name="TeachingLoopAgent",
        description="Adaptive teaching loop using parallel teaching and evaluation",
        sub_agents=[full_iteration],
        max_iterations=10
    )