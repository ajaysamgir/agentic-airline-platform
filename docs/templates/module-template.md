# Module Template

Use this template for every service requirements document. Fill in all sections. Do not skip any section. Agents will use this document as input — incomplete sections produce incomplete output.

---

# {Module Name}

## Purpose

One paragraph describing what this module does and why it exists in the system. Keep it to 3-5 sentences.

---

## Responsibilities

Bullet list of what this module owns and manages. Each item should be a distinct capability.

- Responsibility 1
- Responsibility 2
- Responsibility 3

---

## Features

List the user-facing features this module provides. Each feature maps to at least one API endpoint.

- Feature 1
- Feature 2
- Feature 3

---

## APIs

List every API endpoint this module exposes.

| Method | Path | Description |
|--------|------|-------------|
| POST   | /api/{resource} | Create a new resource |
| GET    | /api/{resource}/{id} | Get resource by ID |
| GET    | /api/{resource}/search | Search resources |

---

## Domain Model

List the main entities and their key attributes.

### {EntityName}

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique identifier |
| field1 | String | Description |
| field2 | LocalDateTime | Description |

---

## Events Published

List Kafka events this module publishes when something important happens.

| Event | Topic | Trigger |
|-------|-------|---------|
| {EntityName}CreatedEvent | {entity}-created | When a new {entity} is created |

---

## Events Consumed

List Kafka events this module listens to from other services.

| Event | Topic | Action Taken |
|-------|-------|-------------|
| {OtherEntity}ConfirmedEvent | {other}-confirmed | Description of what this module does |

---

## Acceptance Criteria

Each acceptance criterion maps directly to a test case. Write them from the user's perspective.

### AC1: {Short title}

Given: {precondition}
When: {action}
Then: {expected result}

### AC2: {Short title}

Given: {precondition}
When: {action}
Then: {expected result}

---

## Error Cases

List the known error scenarios and the expected system behavior.

| Scenario | HTTP Status | Error Message |
|----------|-------------|---------------|
| Resource not found | 404 | "{Resource} with id {id} not found" |
| Invalid input | 400 | "Validation failed: {field} {reason}" |

---

## Dependencies

List other services or external systems this module depends on.

- **{Service Name}:** reason for dependency
