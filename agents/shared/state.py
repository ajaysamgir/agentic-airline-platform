from typing import TypedDict, Optional


class SDLCState(TypedDict):
    """Shared state that flows through every agent in the pipeline."""

    # Input
    service_name: str
    module_description: str

    # Artifacts produced by each agent
    requirements_md: Optional[str]
    architecture_md: Optional[str]
    source_code: Optional[dict]   # filename -> code string
    test_code: Optional[dict]     # filename -> test string
    infra_config: Optional[dict]  # filename -> config string

    # Pipeline control
    current_phase: str            # requirements | architect | developer | tester | devops | done
    human_approved: Optional[bool]
    errors: list
