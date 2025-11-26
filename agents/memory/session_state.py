# the central short term memory for the multi-agent primarily used by orchestrator

from typing import List
from pydantic import BaseModel
from typing import Any

class Milestone(BaseModel):
    objective: str
    content: str

class LearningPlan(BaseModel):
    topic: str
    milestones: List[Milestone]

class EvaluationResult(BaseModel):
    score: int
    mastered: bool
    feedback: str

DEFAULT_SESSION_STATE = {
    "topic": "",
    "research_completed": False,
    "has_learning_plan": False,
    "all_milestones_completed": False,
    "total_milestones": 0,
    "current_step_index": 0,
    "learning_plan": None,
    "latest_eval_result": None,
    "final_report": None,
    "current_milestone_content": "",
    "evaluation_history": [],
    "completed_milestones": []
}

class StateManager:
    @staticmethod
    def _get_attr_or_key(obj: Any, key: str, default: Any = None) -> Any:
        """Helper to safely get value from either a Dict or an Object"""
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    @staticmethod
    def update_state_after_turn(session) -> None:
        state = session.state
        
        # --- 1. HANDLE INITIAL PLAN LOADING ---
        if not state.get("research_completed") and state.get("learning_plan"):
            plan_data = state["learning_plan"]
            
            # Robustly get milestones regardless of data type
            milestones = StateManager._get_attr_or_key(plan_data, 'milestones', [])
            
            state["has_learning_plan"] = True
            state["research_completed"] = True
            state["total_milestones"] = len(milestones)
            state["current_step_index"] = 0
            state["all_milestones_completed"] = False
            print(f"✅ State Update: Plan loaded with {len(milestones)} steps.")

        # --- 2. HANDLE EVALUATION RESULTS ---
        if state.get("latest_eval_result"):
            eval_result = state["latest_eval_result"]        
            
            is_mastered = StateManager._get_attr_or_key(eval_result, 'mastered', False)

            if is_mastered:
                old_idx = state["current_step_index"]
                total = state["total_milestones"]

                current_milestone_obj = None
                if state.get("learning_plan"):
                    milestones = StateManager._get_attr_or_key(state["learning_plan"], 'milestones', [])
                    if old_idx < len(milestones):
                        current_milestone_obj = milestones[old_idx]
                
                milestone_title = (current_milestone_obj.objective 
                                if current_milestone_obj else f"Step {old_idx + 1}")

                history_entry = {
                    "milestone_index": old_idx,
                    "milestone_objective": milestone_title,
                    "score": eval_result.score,
                    "feedback": eval_result.feedback,
                    "misconceptions": eval_result.misconceptions,
                    "mastered": True
                }
                
                state["evaluation_history"].append(history_entry)
                state["completed_milestones"].append(milestone_title)

                print(f"State Update: Milestone {old_idx+1} MASTERED and saved to history (score: {eval_result.score})")

                if old_idx < total:
                    state["current_step_index"] += 1
                    print(f"✅ State Update: Step {old_idx+1} Mastered. Moving to {old_idx+2}.")
                    state["latest_eval_result"] = None 
                
                # Check if we just finished the last step
                if state["current_step_index"] >= total:
                    state["all_milestones_completed"] = True
                    print("🎉 State Update: All milestones completed.")
            else:
                print(f"⚠️ State Update: Step {state['current_step_index']+1} not mastered yet. Retrying.")
            state["latest_eval_result"] = None

        if state.get("has_learning_plan") and not state.get("all_milestones_completed"):
            idx = state["current_step_index"]
            plan = state["learning_plan"]
            milestones = StateManager._get_attr_or_key(plan, 'milestones', [])
            
            if idx < len(milestones):
                current_ms = milestones[idx]
                ms_objective = StateManager._get_attr_or_key(current_ms, "objective", "Unknown")
                ms_content = StateManager._get_attr_or_key(current_ms, "content", "")
                
                # Only update if not already set or changed
                new_content = f"Objective: {ms_objective}. Content: {ms_content}"
                if state.get("current_milestone_content") != new_content:
                    state["current_milestone_content"] = new_content
                    print(f"Updated current_milestone_content for step {idx+1}")