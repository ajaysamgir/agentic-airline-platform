import re

from langchain_core.messages import SystemMessage, HumanMessage

from shared.llm import get_llm
from shared.file_tools import write_file, write_multiple_files
from shared.state import SDLCState
from devops_agent.prompts import DEVOPS_SYSTEM_PROMPT, DEVOPS_USER_PROMPT

# Detect tech from architecture doc
_JAVA_KEYWORDS = ["spring boot", "java", "maven", "pom.xml"]
_KAFKA_KEYWORDS = ["kafka", "event", "published", "consumed"]
_REDIS_KEYWORDS = ["redis", "cache"]


def _detect_tech(architecture_md: str) -> dict:
    text = (architecture_md or "").lower()
    return {
        "technology": "Java 21 + Spring Boot 3" if any(k in text for k in _JAVA_KEYWORDS) else "NestJS (TypeScript)",
        "uses_kafka": "Yes" if any(k in text for k in _KAFKA_KEYWORDS) else "No",
        "uses_redis": "Yes" if any(k in text for k in _REDIS_KEYWORDS) else "No",
    }


def _parse_files_from_response(response_text: str, service_name: str) -> dict:
    files = {}
    pattern = re.compile(r"###\s+([\w/.\-]+)\n```[\w]*\n(.*?)```", re.DOTALL)
    for match in pattern.finditer(response_text):
        file_path = match.group(1).strip()
        content = match.group(2).strip()
        if not file_path.startswith("infra/"):
            file_path = f"infra/{service_name}/{file_path}"
        files[file_path] = content
    return files


def run(state: SDLCState) -> SDLCState:
    """
    DevOps Agent node.
    Input:  state["architecture_md"] (to detect tech/kafka/redis)
    Output: state["infra_config"] — files written to infra/{service}/
    """
    tech = _detect_tech(state.get("architecture_md", ""))

    system_prompt = DEVOPS_SYSTEM_PROMPT
    user_prompt = DEVOPS_USER_PROMPT.format(
        service_name=state["service_name"],
        technology=tech["technology"],
        uses_kafka=tech["uses_kafka"],
        uses_redis=tech["uses_redis"],
    )

    llm = get_llm(model="codestral", temperature=0.1)
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    infra_config = _parse_files_from_response(response.content, state["service_name"])

    if infra_config:
        written = write_multiple_files(infra_config)
        print(f"[DevOpsAgent] Written {len(written)} infra files")
    else:
        fallback_path = f"infra/{state['service_name']}/generated-infra.md"
        write_file(fallback_path, response.content)
        print(f"[DevOpsAgent] Could not parse infra files — raw output saved to {fallback_path}")

    return {
        **state,
        "infra_config": infra_config,
        "current_phase": "done",
    }
