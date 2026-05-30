# Flight Service

## Purpose

Manage airline flight information for the booking platform. This service should capture flight attributes needed for scheduling, searching, and retrieval, while remaining focused on flight domain operations.

The document should help an agent generate implementation code by clarifying the service scope, required capabilities, and the expected customer-facing behavior.

## Features

- Create Flight
- Search Flight
- Get Flight Details

These features define the key service responsibilities and should map directly to endpoints, domain logic, and persistence behavior.

## Acceptance Criteria

### AC1

User can create a flight.

The generated implementation should support adding new flight records with the required flight details.

### AC2

User can search flights.

The generated implementation should support searching flights by route, date, or other relevant flight query parameters.

### AC3

User can retrieve flight details.

The generated implementation should support fetching flight information by a unique flight identifier.
