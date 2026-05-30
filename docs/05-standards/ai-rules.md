# AI Coding Standards

All agents generating code for this project must follow these rules without exception.

---

## Code Quality

- Use Clean Architecture: separate Controller, Service, Repository layers
- All classes must have a single responsibility
- No business logic in controllers
- No database queries in service layer — use repository interfaces only

---

## API Design

- Follow REST conventions strictly
- Use nouns for resource paths: `/api/flights`, `/api/bookings`
- Use HTTP verbs correctly: GET (read), POST (create), PUT (full update), PATCH (partial update), DELETE (remove)
- Always return appropriate HTTP status codes: 200, 201, 400, 404, 500
- All APIs must have OpenAPI/Swagger documentation annotations

---

## Data Transfer

- Never expose domain entities directly in API responses
- Use DTOs for all request and response payloads
- Validate all incoming request DTOs using Bean Validation (`@NotNull`, `@NotBlank`, etc.)

---

## Error Handling

- Use a global exception handler (`@ControllerAdvice` in Spring Boot)
- Return structured error responses: `{ "status": 400, "message": "...", "timestamp": "..." }`
- Never expose stack traces in API responses

---

## Testing

- Every service must have unit tests covering happy path and edge cases
- Use JUnit5 for Java services
- Use Jest for Node services
- Use pytest for Python services
- Minimum coverage target: 80%
- Mock all external dependencies in unit tests

---

## Naming Conventions

- Java: camelCase for methods/variables, PascalCase for classes, UPPER_SNAKE_CASE for constants
- Packages: lowercase, dot-separated: `com.airline.flightservice.controller`
- Database tables: snake_case: `flight_records`, `booking_details`
- Kafka topics: kebab-case: `flight-created`, `booking-confirmed`

---

## Documentation

- Every public method must have a Javadoc or equivalent comment explaining its purpose
- Every service must have a README.md describing how to run it locally
- Every service must document its environment variables

---

## Security

- Never hardcode credentials, API keys, or secrets
- Use environment variables for all configuration
- Validate and sanitize all user inputs

---

## Events (Kafka)

- Event class names: PascalCase suffixed with `Event`: `FlightCreatedEvent`, `BookingConfirmedEvent`
- Event topics: kebab-case matching the event name: `flight-created`, `booking-confirmed`
- All events must include: `eventId`, `eventType`, `timestamp`, `payload`
