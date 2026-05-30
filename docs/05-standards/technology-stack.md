# Technology Stack

This document defines the approved technologies for every service in this project. Agents must not introduce technologies outside this list without explicit approval.

---

## Frontend

- **Framework:** Next.js (React)
- **Language:** TypeScript
- **Styling:** Tailwind CSS

---

## Java Services

- **Language:** Java 21
- **Framework:** Spring Boot 3
- **Build Tool:** Maven
- **ORM:** Spring Data JPA + Hibernate
- **Validation:** Jakarta Bean Validation
- **API Docs:** SpringDoc OpenAPI (Swagger UI)
- **Testing:** JUnit5 + Mockito

---

## Node Services

- **Language:** TypeScript
- **Framework:** NestJS
- **Build Tool:** npm
- **Testing:** Jest

---

## Python Services (Agents)

- **Language:** Python 3.11+
- **Framework:** FastAPI (for APIs), LangGraph (for agents)
- **LLM:** Ollama (local)
- **Testing:** pytest

---

## Messaging

- **Broker:** Apache Kafka
- **Format:** JSON

---

## Database

- **Cache / Session:** Redis
- **Primary DB:** PostgreSQL (per service — each service owns its own schema)

---

## Containers

- **Runtime:** Docker
- **Orchestration:** Docker Compose (local), Kubernetes (future)

---

## AI / Agent Stack

- **IDE:** Cursor
- **Local LLM Runtime:** Ollama
- **Agent Framework:** LangGraph
- **LLM Model:** llama3 (default), codestral (code generation)

---

## CI/CD

- **Pipeline:** GitHub Actions
- **Registry:** GitHub Container Registry (ghcr.io)

---

## Monitoring (Future)

- **Tracing:** Langfuse (agent traces)
- **Metrics:** Prometheus + Grafana
