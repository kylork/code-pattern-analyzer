# Architectural Intent Patterns

This document describes the architectural intent patterns detected by the Code Pattern Analyzer.

## Separation of Concerns

The Separation of Concerns pattern divides a program into distinct sections, each addressing a separate concern. This improves maintainability, reusability, and testability by ensuring that changes to one concern don't affect code that addresses other concerns.

**Detection Criteria:**
- Layer-based separation (e.g., controller, service, repository, model layers)
- Domain-based separation (e.g., organizing code by business domains)
- Component-based separation (e.g., clear boundaries between components)

**Example:**
The layered architecture example demonstrates a clean Separation of Concerns with distinct layers:
- Controllers: Handle user interaction and HTTP requests
- Services: Implement business logic
- Repositories: Handle data access
- Models: Define data structures

## Information Hiding

The Information Hiding pattern (introduced by David Parnas) ensures that components hide their internal implementation details and expose only necessary interfaces. This reduces dependencies, improves modularity, and makes systems more maintainable.

**Detection Criteria:**
- Encapsulation of internal state with private/protected variables
- Use of interfaces and abstract classes to hide implementation details
- Well-defined public APIs with controlled access boundaries
- Use of modules/packages to control visibility

**Example:**
The information hiding example demonstrates these principles with:
- Abstract base classes and interfaces that define contracts
- Implementation classes that hide details behind interfaces
- Private variables with property accessors
- Factory methods that hide implementation class selection
- Client code that depends only on interfaces

## Dependency Inversion

The Dependency Inversion principle states that high-level modules should not depend on low-level modules; both should depend on abstractions. Abstractions should not depend on details; details should depend on abstractions.

**Detection Criteria:**
- Use of interfaces/abstract classes
- Dependency injection mechanisms
- Factories or service providers
- Layers depending on abstractions rather than concrete implementations

**Example:**
This principle is demonstrated in the information hiding example through:
- Service interfaces that are independent of their implementations
- Repository abstractions that hide data access details
- Factory classes that create and inject dependencies
- Clients that program to interfaces, not implementations