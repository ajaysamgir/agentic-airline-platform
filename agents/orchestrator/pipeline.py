import sys
import os

# Allow imports from agents/ root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from shared.state import SDLCState
import requirements_agent.agent as requirements_agent
import architect_agent.agent as architect_agent
import developer_agent.agent as developer_agent
import tester_agent.agent as tester_agent
import devops_agent.agent as devops_agent


def human_review_gate(state: SDLCState) -> SDLCState:
    """
    Human-in-the-loop checkpoint after the Architect Agent.
    Pauses execution and waits for human approval before code generation begins.
    In terminal mode: prompts the user directly.
    """
    print("\n" + "=" * 60)
    print("HUMAN REVIEW REQUIRED — Architecture Document")
    print("=" * 60)
    print(f"\nService: {state['service_name']}")
    print(f"\nArchitecture saved to: modules/{state['service_name']}/docs/architecture.md")
    print("\nReview the architecture document before proceeding to code generation.")
    print("\nOptions:")
    print("  [a] Approve — proceed to code generation")
    print("  [r] Reject  — re-run architect agent")
    print("  [q] Quit    — stop pipeline")

    while True:
        choice = input("\nYour decision [a/r/q]: ").strip().lower()
        if choice == "a":
            print("\n[HumanReview] Approved. Proceeding to Developer Agent.")
            return {**state, "human_approved": True, "current_phase": "developer"}
        elif choice == "r":
            print("\n[HumanReview] Rejected. Re-running Architect Agent.")
            return {**state, "human_approved": False, "current_phase": "architect"}
        elif choice == "q":
            print("\n[HumanReview] Pipeline stopped by user.")
            sys.exit(0)
        else:
            print("Invalid input. Please enter a, r, or q.")


def route_after_review(state: SDLCState) -> str:
    """Conditional edge: route based on human approval decision."""
    if state.get("human_approved"):
        return "developer"
    return "architect"


def build_pipeline() -> StateGraph:
    """Build and compile the full SDLC LangGraph pipeline."""
    graph = StateGraph(SDLCState)

    graph.add_node("requirements", requirements_agent.run)
    graph.add_node("architect",    architect_agent.run)
    graph.add_node("human_review", human_review_gate)
    graph.add_node("developer",    developer_agent.run)
    graph.add_node("tester",       tester_agent.run)
    graph.add_node("devops",       devops_agent.run)

    graph.set_entry_point("requirements")
    graph.add_edge("requirements", "architect")
    graph.add_edge("architect",    "human_review")
    graph.add_conditional_edges(
        "human_review",
        route_after_review,
        {"developer": "developer", "architect": "architect"},
    )
    graph.add_edge("developer", "tester")
    graph.add_edge("tester",    "devops")
    graph.add_edge("devops",    END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


def run_pipeline(service_name: str, module_description: str) -> SDLCState:
    """Entry point: run the full SDLC pipeline for a service."""
    print(f"\n{'=' * 60}")
    print(f"SDLC Pipeline — {service_name}")
    print(f"{'=' * 60}\n")

    pipeline = build_pipeline()

    initial_state: SDLCState = {
        "service_name": service_name,
        "module_description": module_description,
        "requirements_md": None,
        "architecture_md": None,
        "source_code": None,
        "test_code": None,
        "infra_config": None,
        "current_phase": "requirements",
        "human_approved": None,
        "errors": [],
    }

    config = {"configurable": {"thread_id": service_name}}
    final_state = pipeline.invoke(initial_state, config=config)

    print(f"\n{'=' * 60}")
    print(f"Pipeline complete for: {service_name}")
    print(f"{'=' * 60}")
    print(f"  requirements.md  → modules/{service_name}/docs/requirements.md")
    print(f"  architecture.md  → modules/{service_name}/docs/architecture.md")
    print(f"  source code      → modules/{service_name}/src/")
    print(f"  tests            → modules/{service_name}/src/test/")
    print(f"  infra            → infra/{service_name}/")

    return final_state


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the SDLC multi-agent pipeline")
    parser.add_argument("--service", required=True, help="Service name, e.g. booking-service")
    parser.add_argument("--description", required=True, help="Plain-English description of the service")
    args = parser.parse_args()

    run_pipeline(service_name=args.service, module_description=args.description)
