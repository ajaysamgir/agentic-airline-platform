import re

from langchain_core.messages import SystemMessage, HumanMessage

from shared.llm import get_llm
from shared.file_tools import write_file, write_multiple_files, read_standards
from shared.state import SDLCState
from tester_agent.prompts import TESTER_SYSTEM_PROMPT, TESTER_USER_PROMPT


def _summarize_source(source_code: dict) -> str:
    """Build a summary of source file paths and key class names for the prompt."""
    if not source_code:
        return "No source code provided."
    lines = ["Source files:"]
    for path in sorted(source_code.keys()):
        lines.append(f"  - {path}")
    # Include full content of service and controller files only (avoid token limit)
    lines.append("\nKey files (full content):")
    for path, code in source_code.items():
        if "Controller" in path or "Service" in path:
            lines.append(f"\n### {path}\n```java\n{code}\n```")
    return "\n".join(lines)


def _parse_files_from_response(response_text: str, service_name: str) -> dict:
    files = {}
    pattern = re.compile(r"###\s+([\w/.\-]+)\n```[\w]*\n(.*?)```", re.DOTALL)
    for match in pattern.finditer(response_text):
        file_path = match.group(1).strip()
        code = match.group(2).strip()
        if not file_path.startswith("modules/"):
            file_path = f"modules/{service_name}/src/test/java/{file_path}"
        files[file_path] = code
    return files


def run(state: SDLCState) -> SDLCState:
    """
    Tester Agent node.
    Input:  state["source_code"]
    Output: state["test_code"] — test files written to modules/{service}/src/test/
    """
    standards = read_standards()

    system_prompt = TESTER_SYSTEM_PROMPT.format(ai_rules=standards["ai_rules"])
    user_prompt = TESTER_USER_PROMPT.format(
        service_name=state["service_name"],
        source_code_summary=_summarize_source(state.get("source_code", {})),
    )

    llm = get_llm(model="codestral", temperature=0.1)
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    test_code = _parse_files_from_response(response.content, state["service_name"])

    if test_code:
        written = write_multiple_files(test_code)
        print(f"[TesterAgent] Written {len(written)} test files")
    else:
        fallback_path = f"modules/{state['service_name']}/src/test/generated-tests.md"
        write_file(fallback_path, response.content)
        print(f"[TesterAgent] Could not parse test files — raw output saved to {fallback_path}")

    return {
        **state,
        "test_code": test_code,
        "current_phase": "devops",
    }
