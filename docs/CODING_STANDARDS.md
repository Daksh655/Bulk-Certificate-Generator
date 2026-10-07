# Coding Standards

## General

- Keep implementation simple.
- Do not over-engineer.
- Follow the documented architecture.
- Do not introduce technologies not specified in the requirements.
- Write readable and maintainable code.
- Use meaningful names.
- Keep functions focused on one responsibility.

## Backend

Use the following separation:

API / Router
|
Service
|
Repository / Database
|
SQLAlchemy

Do not put business logic directly inside route handlers
when the logic belongs in a service.

## Validation

Use Pydantic schemas for request and response validation.

## Database

Use SQLAlchemy models and sessions.

Do not scatter raw SQL throughout the application.

## Error Handling

Return meaningful HTTP errors.

Do not expose internal stack traces to API clients.

## Certificate Generation

Certificate generation must be isolated inside a dedicated service.

## Background Processing

Background processing must be controlled and must isolate
individual certificate failures.

## Frontend

Use reusable React components.

Keep API communication separate from UI components where practical.

Avoid unnecessary state management libraries.

## Comments

Do not write comments for obvious code.

Comments should explain reasoning when necessary.

## Dependencies

Do not add libraries unless they solve a real requirement.