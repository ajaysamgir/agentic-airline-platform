# Study Notes: Multi-Agent SDLC System
## How It Works + AI/ML Concepts for Interviews

---

# PART 1: HOW CURSOR RULES WORK INTERNALLY

## What Happens When You Type `@developer-agent`

Most developers think Cursor "switches modes" when you use a rule. That is not what happens. Here is the real mechanism:

```
Your message:
  "@developer-agent generate Spring Boot service for this architecture"

What Cursor actually sends to the LLM:
  [System Prompt = developer-agent.mdc content]
  +
  [Project context = 00-project-context.mdc content]
  +
  [Your message]
  +
  [Open files in editor]
```

The `.mdc` file content is **prepended** to the LLM's context window before your message. The AI never "becomes" a different agent — it receives different instructions at the start of its context that shape its behavior.

---

## The Context Window — The Most Important Concept

```
┌────────────────────────────────────────────────────────┐
│                   LLM Context Window                   │
│                                                        │
│  [1] System Rules (alwaysApply rules always here)      │
│      00-project-context.mdc                            │
│                                                        │
│  [2] Agent Persona (when @-mentioned)                  │
│      developer-agent.mdc                               │
│                                                        │
│  [3] Open Files in Editor                              │
│      architecture.md (the file you have open)         │
│                                                        │
│  [4] Your Message                                      │
│      "generate Spring Boot service"                    │
│                                                        │
│  [5] Conversation History                              │
│      Previous messages in this chat                    │
└────────────────────────────────────────────────────────┘
```

**Why this matters for interviews:**
> "The context window is finite. Every rule file, every open file, every message consumes tokens. If you add too many rules, the model runs out of space for your actual code. Good prompt engineering means being selective about what you put in context."

---

## The Four Rule Types — How They Actually Differ

| Type | frontmatter | When loaded into context | Use case |
|------|-------------|--------------------------|----------|
| Always Apply | `alwaysApply: true` | Every single request | Project standards, tech stack |
| Auto-Attached | `globs: ["**/*.java"]` | When matching file is open | Java-specific rules for Java files |
| Agent-Requested | `description: "..."`, no globs | When Cursor decides it's relevant | Rules that apply to specific tasks |
| Manual | No description, no globs | Only when `@rule-name` is typed | Agent personas |

Our `00-project-context.mdc` uses `alwaysApply: true` — it loads on every request.
Our 5 agent `.mdc` files use manual mode — they only load when you `@mention` them.

---

## Why We Use `.mdc` and Not `.md`

`.mdc` = Markdown Cursor format. It supports YAML frontmatter:

```
---
description: "Architect Agent"
alwaysApply: false
---

# Rest of the rule content...
```

A plain `.md` file in `.cursor/rules/` is **ignored by the rules system** — Cursor only processes `.mdc` files with valid frontmatter.

---

## How `00-project-context.mdc` Acts as the "Brain Stem"

Every single Cursor conversation in this project starts with:

1. Tech stack loaded into context (Java 21, Spring Boot 3, etc.)
2. Folder structure rules loaded
3. Coding standards loaded

This means even if you forget to mention the tech stack, the AI already knows it. This is why our standards docs (`ai-rules.md`, `technology-stack.md`) had to be created **before** the rules — the rules reference those files.

```
00-project-context.mdc  →  references  →  docs/05-standards/ai-rules.md
                        →  references  →  docs/05-standards/technology-stack.md
```

If the standards files don't exist, the rule references them but they're empty — the agent produces inconsistent output.

---

# PART 2: HOW THE LANGGRAPH PYTHON PIPELINE WORKS INTERNALLY

## LangGraph Fundamentals

LangGraph models your workflow as a **directed graph**:

```
Nodes = functions (your agents)
Edges = connections between agents
State = shared data that flows through all nodes
```

Think of it like a factory assembly line:

```
Raw Material (module description)
      ↓
Station 1: Requirements Agent   →  produces requirements.md
      ↓
Station 2: Architect Agent      →  produces architecture.md
      ↓
Quality Check: Human Review     →  approve or reject
      ↓
Station 3: Developer Agent      →  produces source code
      ↓
Station 4: Tester Agent         →  produces test files
      ↓
Station 5: DevOps Agent         →  produces infra config
      ↓
Finished Product
```

---

## The State Object — How Agents Share Data

The `SDLCState` TypedDict in `agents/shared/state.py` is the single shared memory:

```python
class SDLCState(TypedDict):
    service_name: str               # "flight-service"
    module_description: str         # "Manages flight data"
    requirements_md: Optional[str]  # Written by RequirementsAgent
    architecture_md: Optional[str]  # Written by ArchitectAgent
    source_code: Optional[dict]     # Written by DeveloperAgent
    test_code: Optional[dict]       # Written by TesterAgent
    infra_config: Optional[dict]    # Written by DevOpsAgent
    current_phase: str              # Tracks where we are
    human_approved: Optional[bool]  # Tracks HITL decision
    errors: list                    # Accumulates any errors
```

**Key rule:** Every agent node receives the full state and returns an updated version of it. Agents never talk to each other directly — they only communicate through state.

```
RequirementsAgent:  reads  state["module_description"]
                    writes state["requirements_md"]

ArchitectAgent:     reads  state["requirements_md"]
                    writes state["architecture_md"]

DeveloperAgent:     reads  state["architecture_md"]
                    writes state["source_code"]
```

This is called the **blackboard pattern** in multi-agent systems — one shared data store, multiple agents reading/writing.

---

## How Each Python Agent Works (The Pattern)

Every agent follows the same 4-step pattern:

```python
def run(state: SDLCState) -> SDLCState:

    # Step 1: Read inputs from state + load standards
    requirements_md = state["requirements_md"]
    standards = read_standards()   # ai-rules.md, tech-stack.md, template.md

    # Step 2: Build the prompt (system + user)
    system_prompt = SYSTEM_PROMPT.format(ai_rules=standards["ai_rules"])
    user_prompt   = USER_PROMPT.format(requirements_md=requirements_md)

    # Step 3: Call the LLM (Ollama)
    llm = get_llm(model="codestral", temperature=0.1)
    response = llm.invoke([SystemMessage(system_prompt), HumanMessage(user_prompt)])

    # Step 4: Write output to file + update state
    write_file("modules/flight-service/docs/architecture.md", response.content)
    return {**state, "architecture_md": response.content, "current_phase": "human_review"}
```

---

## Human-in-the-Loop (HITL) — Why It's Critical

After the Architect Agent produces `architecture.md`, the pipeline **pauses** and asks you:

```
[a] Approve — proceed to code generation
[r] Reject  — re-run architect agent
[q] Quit    — stop pipeline
```

Why is this important? Because **code generation is expensive and hard to undo**. A bad architecture produces hundreds of lines of wrong code. Reviewing the architecture first (a 2-minute read) prevents hours of cleanup.

This is a core principle in production AI systems: **never let an agent take an irreversible expensive action without human approval.**

LangGraph supports this natively through `interrupt_before` and `interrupt_after` in its checkpointing system.

---

## Conditional Edges — The Routing Logic

After human review, the pipeline branches:

```python
graph.add_conditional_edges(
    "human_review",           # from this node
    route_after_review,       # call this function to decide
    {
        "developer": "developer",   # if approved → go to developer
        "architect": "architect",   # if rejected → go back to architect
    }
)
```

The routing function simply reads state:
```python
def route_after_review(state: SDLCState) -> str:
    if state.get("human_approved"):
        return "developer"
    return "architect"
```

This pattern (conditional edges + state-based routing) is how LangGraph implements retry loops, fallback paths, and quality gates.

---

## The MemorySaver — Checkpointing

```python
checkpointer = MemorySaver()
pipeline = graph.compile(checkpointer=checkpointer)
```

This saves the entire state after every node executes. If the pipeline crashes mid-way (say, at the Developer Agent), you can resume from the last saved state instead of re-running everything from scratch.

For production: replace `MemorySaver` (in-memory, lost on restart) with `PostgresSaver` (persistent).

---

# PART 3: AI/ML CONCEPTS YOU MUST KNOW

## 1. Large Language Models (LLMs) — What They Actually Are

An LLM is a **next-token predictor** trained on massive text datasets. It does not "understand" code or requirements — it predicts the most statistically likely continuation of a given text sequence.

When you prompt it "Generate a Spring Boot controller", it produces code because it has seen millions of Spring Boot controllers in its training data and predicts the tokens that typically follow that instruction.

**Interview answer:**
> "LLMs are probabilistic text completion engines. They generate the statistically most likely output for a given input. They do not execute code, access the internet, or maintain state between calls. Every call is stateless."

---

## 2. Temperature — Controlling Randomness

```python
get_llm(model="codestral", temperature=0.1)   # code generation
get_llm(model="codestral", temperature=0.3)   # requirements writing
```

Temperature controls how "creative" or "random" the output is:

```
temperature = 0.0  →  always picks the single most likely token (deterministic)
temperature = 0.1  →  nearly deterministic, small variation (good for code)
temperature = 0.5  →  balanced (good for documentation)
temperature = 1.0  →  highly creative / random (good for brainstorming)
temperature > 1.0  →  increasingly chaotic / unreliable
```

**Why we use 0.1 for code:** Code must be syntactically correct and consistent. High temperature produces variable, often broken code. Low temperature produces predictable, reproducible output.

**Why we use 0.3 for requirements:** Requirements benefit from slight variation so the model explores different phrasings and doesn't just repeat the same structure every time.

---

## 3. System Prompt vs User Prompt

```
System Prompt = the instructions and role given to the AI before the conversation
User Prompt   = the actual request / question
```

In our agents:

```python
llm.invoke([
    SystemMessage(content="You are a Senior Architect. Follow these standards: ..."),
    HumanMessage(content="Design the architecture for flight-service"),
])
```

The `SystemMessage` sets the **persona and constraints**. The `HumanMessage` is the **task**. Models are trained to follow system prompts more strictly than user prompts — that's why we put coding standards in the system prompt.

---

## 4. Tokens — The Currency of LLMs

Everything fed into an LLM is converted to **tokens** (roughly 0.75 words per token in English, fewer for code).

```
"Spring Boot Controller"  ≈  4 tokens
A 100-line Java file      ≈  500-800 tokens
Our ai-rules.md file      ≈  600 tokens
Our architecture.md       ≈  400 tokens
```

**Context window limit** = maximum tokens the model can process at once.

- GPT-4o: 128,000 tokens
- Claude 3.5 Sonnet: 200,000 tokens
- codestral (Ollama): 32,000 tokens

**This is why in `tester_agent/agent.py` we only include Controller and Service files in the prompt** — including ALL source files would exceed the context window:

```python
for path, code in source_code.items():
    if "Controller" in path or "Service" in path:  # selective inclusion
        lines.append(f"\n### {path}\n```java\n{code}\n```")
```

---

## 5. Prompt Engineering — The Core Skill

Prompt engineering is designing inputs that reliably produce the desired outputs from an LLM. Key techniques used in this project:

**Role prompting:**
```
"You are a Senior Java Architect with 10 years of microservices experience."
```
Models produce better output when given a specific expert persona.

**Constraint injection:**
```
"Choose technologies ONLY from the approved stack. Never introduce new dependencies."
```
Explicit constraints prevent hallucination and scope creep.

**Output format specification:**
```
"Output each file as ### path/to/File.java followed by a java code block."
```
Structured output formats make parsing reliable. Without this, the model produces free-form text that's hard to extract from.

**Chain-of-thought (implicit):**
By chaining agents (requirements → architecture → code), we force the model to reason step by step instead of jumping straight to code. Each step builds on the previous — this improves quality significantly.

---

## 6. Agentic AI — What Makes It "Agentic"

A simple LLM call: input → LLM → output. Done.

An **agent** adds:
1. **Tools** — the ability to take actions (read files, write files, call APIs)
2. **Memory** — state that persists between steps
3. **Planning** — breaking a goal into sub-tasks
4. **Feedback loops** — checking its own output and retrying

Our pipeline is agentic because:
- Agents read/write files (tools)
- State flows between agents (memory)
- The pipeline breaks "build a service" into 5 sub-tasks (planning)
- The human review gate and reject path form a feedback loop

---

## 7. RAG — Retrieval-Augmented Generation

Not used yet but important to know for interviews.

**Problem:** LLMs have a training cutoff and don't know your specific codebase.

**Solution:** Before calling the LLM, retrieve relevant documents from a knowledge base and inject them into the prompt.

```
User: "How should I implement the booking service?"
         ↓
RAG system searches your docs/  →  finds booking-service-requirements.md
         ↓
Injects that document into the prompt
         ↓
LLM answers with knowledge of YOUR specific requirements
```

**For this project:** A future enhancement would be to use RAG so agents can search all previous service implementations before generating new ones — ensuring consistency across services.

---

## 8. Hallucination — The Core Risk of LLMs

LLMs sometimes generate **plausible-sounding but incorrect information** — method names that don't exist, dependencies with wrong versions, import paths that are wrong.

This is why your `overall-plan.md` says:
> "Never trust generated code. Check: Naming, Structure, Error Handling, Tests, API Design."

**Mitigation strategies used in this project:**
- `temperature=0.1` — reduces randomness, less hallucination
- Coding standards in system prompt — constrains output to known patterns
- Human review gate — you verify architecture before code is generated
- Structured output format — parseable output is easier to validate

---

## 9. Multi-Agent Patterns — The Three Main Types

```
1. Sequential Pipeline (what we built)
   RA → AA → DA → TA → DO
   Simple, predictable, easy to debug

2. Supervisor Pattern
   Supervisor decides which specialist to call
   More flexible, handles complex routing

3. Peer-to-Peer / Swarm
   Agents communicate directly with each other
   Most powerful, hardest to control/debug
```

We chose **sequential pipeline** because:
- The SDLC naturally has a sequence: requirements before architecture, architecture before code
- Easier to debug (you know exactly which agent produced what)
- Easier to add human review gates at specific points
- Sufficient for a portfolio/learning project

---

## 10. Ollama + codestral — Your Local LLM Stack

**Ollama** is a runtime that lets you run open-source LLMs locally on your machine. No API key, no cost, no data leaving your computer.

**codestral** is Mistral AI's code-specialized model. It is trained specifically on code and outperforms general-purpose models on code generation tasks.

```bash
ollama serve          # starts the Ollama server on localhost:11434
ollama pull codestral # downloads the codestral model (~9GB)
ollama list           # lists downloaded models
```

In `agents/shared/llm.py`:
```python
from langchain_ollama import ChatOllama
llm = ChatOllama(model="codestral", temperature=0.1)
# This connects to http://localhost:11434 automatically
```

**Tradeoff vs OpenAI API:**
- Ollama: free, private, slower, smaller models, no internet required
- OpenAI: costs money, much smarter models, faster, data leaves your machine

---

# PART 4: INTERVIEW QUESTIONS AND ANSWERS

## "What is a context window and why does it matter?"
> The context window is the maximum amount of text (measured in tokens) that a language model can process in a single call. It includes the system prompt, conversation history, open files, and the user's message. When context exceeds the limit, older content is truncated, causing the model to "forget" earlier parts of the conversation. In a multi-agent pipeline, managing context window size is critical — we selectively include only the most relevant files in each prompt rather than dumping everything.

## "What is prompt engineering?"
> Prompt engineering is the practice of designing LLM inputs to reliably produce desired outputs. Key techniques include role prompting (giving the model a specific expert persona), constraint injection (explicit rules the model must follow), output format specification (telling the model exactly how to structure its response), and chain-of-thought prompting (breaking complex tasks into sequential steps). Good prompt engineering improves output quality, reduces hallucination, and makes outputs consistent and parseable.

## "What is the difference between a simple LLM call and an agentic workflow?"
> A simple LLM call is stateless: input goes in, output comes out, and nothing persists. An agentic workflow adds tools (the ability to take actions like reading/writing files), memory (state that persists across steps), planning (decomposing goals into sub-tasks), and feedback loops (checking output quality and retrying). LangGraph enables agentic workflows by modeling them as stateful directed graphs where each node is an agent function and edges define the flow.

## "What is RAG and when would you use it?"
> Retrieval-Augmented Generation solves the problem of LLMs not knowing your specific codebase or documentation. Before calling the LLM, a retrieval step searches a knowledge base (your docs, your code, past decisions) and injects relevant documents into the prompt. This grounds the model's response in your actual context rather than general training knowledge. I would use RAG in this project when the number of services grows — so agents can search past service implementations to ensure consistency.

## "What is temperature in an LLM and how do you choose it?"
> Temperature controls the randomness of token selection. Low temperature (0.0-0.2) produces deterministic, consistent outputs — ideal for code generation where syntax must be correct. High temperature (0.7-1.0) produces creative, varied outputs — better for brainstorming and documentation. I use 0.1 for all code generation in this project and 0.3 for requirements writing.

## "What is the blackboard pattern in multi-agent systems?"
> The blackboard pattern is an architectural approach where multiple agents share a single, central data store (the blackboard) instead of communicating directly with each other. Each agent reads from and writes to the shared store. In our LangGraph pipeline, the SDLCState TypedDict is the blackboard — every agent reads the outputs of previous agents from state and writes its own outputs back to state. Agents never call each other directly.

## "What is human-in-the-loop (HITL) and why is it important?"
> Human-in-the-loop means pausing an automated pipeline at a decision point and waiting for human approval before proceeding. It's critical for actions that are expensive, irreversible, or high-risk. In our pipeline, we pause after the Architect Agent because generating code from a flawed architecture wastes significant compute and produces large amounts of incorrect code that's hard to clean up. The human reviews the architecture document (a 2-minute task) and either approves or requests a revision.

---

# PART 5: QUICK REFERENCE — WHAT LIVES WHERE

```
.cursor/rules/
├── 00-project-context.mdc      Always loaded. Tech stack + folder structure.
├── requirements-agent.mdc      @requirements-agent  → requirements.md
├── architect-agent.mdc         @architect-agent     → architecture.md
├── developer-agent.mdc         @developer-agent     → source code
├── tester-agent.mdc            @tester-agent        → test files
└── devops-agent.mdc            @devops-agent        → Dockerfile + CI

agents/
├── shared/
│   ├── state.py        SDLCState TypedDict — the shared blackboard
│   ├── llm.py          Ollama client factory
│   └── file_tools.py   Read/write files relative to repo root
├── requirements_agent/ agent.py + prompts.py
├── architect_agent/    agent.py + prompts.py
├── developer_agent/    agent.py + prompts.py
├── tester_agent/       agent.py + prompts.py
├── devops_agent/       agent.py + prompts.py
└── orchestrator/
    └── pipeline.py     LangGraph StateGraph + HITL gate

docs/
├── 05-standards/
│   ├── ai-rules.md           Coding standards all agents follow
│   └── technology-stack.md   Approved technologies
└── templates/
    └── module-template.md    Template for every requirements.md
```
