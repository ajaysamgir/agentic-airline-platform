# Flight Service Architecture

## Purpose

Manage airline flight information for a booking platform. The service stores flight details, supports new flight creation, retrieves flight data by identifier, and enables search across routes and schedules.

The document should help an agent generate code with a clear understanding of service responsibilities, expected domain entities, and API behavior.

---

## Technology

- Java 21
- Spring Boot 3

These are the preferred implementation technologies and should guide code generation decisions for framework usage, configuration, and dependency selection.

---

## Domain Model

Flight

Attributes:

- id
- flightNumber
- source
- destination
- departureTime
- arrivalTime
- availableSeats

The `Flight` entity is the central domain object. It represents a scheduled flight with a unique identity, route data, timing, and the number of available seats.

---

## APIs

### Create Flight

POST /api/flights

Request payload should include flight details needed to register a new flight in the system.

### Get Flight

GET /api/flights/{id}

Retrieves a specific flight by its unique identifier.

### Search Flights

GET /api/flights/search

Searches flights by route, date, or other query parameters. This endpoint supports finding available flights without requiring a specific flight ID.

The API section clarifies the contract the generated code should implement, including endpoints and their intended responsibilities.

---

## Future Events

Published:

- FlightCreated

Consumed:

- None

This service publishes a `FlightCreated` event whenever a new flight is created. No external events are consumed by this service yet.

---

## Error Handling

404 - Flight Not Found

400 - Invalid Request

500 - Internal Server Error

The generated code should include standard error responses for missing resources, invalid input, and unexpected server failures.
