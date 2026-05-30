import re

from langchain_core.messages import SystemMessage, HumanMessage

from shared.llm import get_llm
from shared.file_tools import write_file, write_multiple_files, read_standards
from shared.state import SDLCState
from developer_agent.prompts import DEVELOPER_SYSTEM_PROMPT, DEVELOPER_USER_PROMPT


def _parse_files_from_response(response_text: str, service_name: str) -> dict:
    """
    Parse LLM response into a dict of {relative_path: code_content}.
    Looks for ### path/to/File.java markers followed by code blocks.
    """
    files = {}
    pattern = re.compile(r"###\s+([\w/.\-]+)\n```[\w]*\n(.*?)```", re.DOTALL)
    for match in pattern.finditer(response_text):
        file_path = match.group(1).strip()
        code = match.group(2).strip()
        # Ensure path is under modules/{service_name}/src/
        if not file_path.startswith("modules/"):
            file_path = f"modules/{service_name}/src/{file_path}"
        files[file_path] = code
    return files


def run(state: SDLCState) -> SDLCState:
    """
    Developer Agent node.
    Input:  state["architecture_md"]
    Output: state["source_code"] — all source files written to modules/{service}/src/
    """
    standards = read_standards()

    system_prompt = DEVELOPER_SYSTEM_PROMPT.format(ai_rules=standards["ai_rules"])
    user_prompt = DEVELOPER_USER_PROMPT.format(
        service_name=state["service_name"],
        architecture_md=state["architecture_md"],
    )

    llm = get_llm(model="codestral", temperature=0.1)
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    source_code = _parse_files_from_response(response.content, state["service_name"])

    if source_code:
        written = write_multiple_files(source_code)
        print(f"[DeveloperAgent] Written {len(written)} files")
    else:
        # Fallback: save raw response so nothing is lost
        fallback_path = f"modules/{state['service_name']}/src/generated-output.md"
        write_file(fallback_path, response.content)
        print(f"[DeveloperAgent] Could not parse files — raw output saved to {fallback_path}")

    return {
        **state,
        "source_code": source_code,
        "current_phase": "tester",
    }
