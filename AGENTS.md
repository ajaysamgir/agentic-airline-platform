# AGENTS.md — agentic-airline-platform

This file documents all AI agents available in this project, how to invoke them, and what each one does.

---

## Two Ways to Use Agents

### 1. Interactive Mode (Cursor Rules)
Invoke agents directly inside Cursor chat using `@agent-name`. The agent persona is loaded and Cursor responds in that role.

### 2. Autonomous Mode (LangGraph Pipeline)
Run the Python pipeline from the terminal. Agents execute in sequence and write output files automatically.

```bash
cd agents
python orchestrator/pipeline.py --service booking-service --description "Manages flight reservations"
```

---

## Available Agents

### Requirements Agent
**Role:** Business Analyst  
**Cursor trigger:** `@requirements-agent`  
**Python:** `agents/requirements_agent/agent.py`  
**Input:** Module name + plain-English description  
**Output:** `modules/{service}/docs/requirements.md`

**Example Cursor usage:**
```
@requirements-agent

Create requirements for the booking-service.
It should allow users to create, cancel, and confirm flight bookings.
```

---

### Architect Agent
**Role:** Senior Software Architect  
**Cursor trigger:** `@architect-agent`  
**Python:** `agents/architect_agent/agent.py`  
**Input:** `modules/{service}/docs/requirements.md`  
**Output:** `modules/{service}/docs/architecture.md`

**Example Cursor usage:**
```
@architect-agent

Design the architecture for this service:
[paste requirements.md content]
```

---

### Developer Agent
**Role:** Senior Developer  
**Cursor trigger:** `@developer-agent`  
**Python:** `agents/developer_agent/agent.py`  
**Input:** `modules/{service}/docs/architecture.md`  
**Output:** All source code files in `modules/{service}/src/`

**Example Cursor usage:**
```
@developer-agent

Generate the Spring Boot service for this architecture:
[paste architecture.md content or open the file]
```

---

### Tester Agent
**Role:** QA Engineer  
**Cursor trigger:** `@tester-agent`  
**Python:** `agents/tester_agent/agent.py`  
**Input:** Source code files  
**Output:** Test files in `modules/{service}/src/test/`

**Example Cursor usage:**
```
@tester-agent

Generate JUnit5 tests for the FlightService and FlightController classes.
```

---

### DevOps Agent
**Role:** DevOps Engineer  
**Cursor trigger:** `@devops-agent`  
**Python:** `agents/devops_agent/agent.py`  
**Input:** Service name  
**Output:** `infra/{service}/Dockerfile`, `docker-compose.yml`, GitHub Actions CI

**Example Cursor usage:**
```
@devops-agent

Generate Dockerfile, docker-compose, and GitHub Actions CI for flight-service (Java 21, Spring Boot 3).
```

---

## Full SDLC Pipeline (Manual — Cursor)

```
1. @requirements-agent  →  modules/{service}/docs/requirements.md
2. @architect-agent     →  modules/{service}/docs/architecture.md
3. @developer-agent     →  modules/{service}/src/
4. @tester-agent        →  modules/{service}/src/test/
5. @devops-agent        →  infra/{service}/
```

---

## Full SDLC Pipeline (Autonomous — Python)

```bash
# Install dependencies
cd agents
pip install -r requirements.txt

# Make sure Ollama is running
ollama serve
ollama pull codestral

# Run the full pipeline
python orchestrator/pipeline.py \
  --service flight-service \
  --description "Manages airline flight information"
```

The pipeline runs all 5 agents in sequence with a human review gate after the Architect Agent.

---

## Standards All Agents Follow

- `docs/05-standards/ai-rules.md` — coding standards
- `docs/05-standards/technology-stack.md` — approved technologies
- `docs/templates/module-template.md` — requirements document structure
