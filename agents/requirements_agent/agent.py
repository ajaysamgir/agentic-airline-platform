from langchain_core.messages import SystemMessage, HumanMessage

from shared.llm import get_llm
from shared.file_tools import write_file, read_standards
from shared.state import SDLCState
from requirements_agent.prompts import REQUIREMENTS_SYSTEM_PROMPT, REQUIREMENTS_USER_PROMPT


def run(state: SDLCState) -> SDLCState:
    """
    Requirements Agent node.
    Input:  state["service_name"], state["module_description"]
    Output: state["requirements_md"] — written to modules/{service}/docs/requirements.md
    """
    standards = read_standards()

    system_prompt = REQUIREMENTS_SYSTEM_PROMPT.format(
        ai_rules=standards["ai_rules"],
        module_template=standards["module_template"],
    )
    user_prompt = REQUIREMENTS_USER_PROMPT.format(
        service_name=state["service_name"],
        module_description=state["module_description"],
    )

    llm = get_llm(model="codestral", temperature=0.3)
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    requirements_md = response.content

    output_path = f"modules/{state['service_name']}/docs/requirements.md"
    write_file(output_path, requirements_md)

    print(f"[RequirementsAgent] Written to {output_path}")

    return {
        **state,
        "requirements_md": requirements_md,
        "current_phase": "architect",
    }
