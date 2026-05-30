from langchain_core.messages import SystemMessage, HumanMessage

from shared.llm import get_llm
from shared.file_tools import write_file, read_standards
from shared.state import SDLCState
from architect_agent.prompts import ARCHITECT_SYSTEM_PROMPT, ARCHITECT_USER_PROMPT


def run(state: SDLCState) -> SDLCState:
    """
    Architect Agent node.
    Input:  state["requirements_md"]
    Output: state["architecture_md"] — written to modules/{service}/docs/architecture.md
    """
    standards = read_standards()

    system_prompt = ARCHITECT_SYSTEM_PROMPT.format(
        tech_stack=standards["tech_stack"],
        ai_rules=standards["ai_rules"],
    )
    user_prompt = ARCHITECT_USER_PROMPT.format(
        service_name=state["service_name"],
        requirements_md=state["requirements_md"],
    )

    llm = get_llm(model="codestral", temperature=0.1)
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    architecture_md = response.content

    output_path = f"modules/{state['service_name']}/docs/architecture.md"
    write_file(output_path, architecture_md)

    print(f"[ArchitectAgent] Written to {output_path}")

    return {
        **state,
        "architecture_md": architecture_md,
        "current_phase": "human_review",
    }
