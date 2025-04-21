# Repository-Based Strategy Pattern

## Overview

The Repository-Based Strategy Pattern is an extension of the classic Strategy pattern that centralizes the creation and registration of strategies in a dedicated repository class. This variant enhances the basic Strategy pattern with centralized management, runtime registration, and decoupled strategy selection.

## Structure

### Components

1. **Strategy Interface/Abstract Class**: Defines the common interface for all concrete strategies.

2. **Concrete Strategies**: Implement the strategy interface with specific algorithms.

3. **Strategy Repository**: Central registry that manages strategy creation and lookup:
   - Provides registration methods for adding strategies
   - Stores strategies by key or identifier
   - Offers factory methods to create or retrieve strategy instances
   - May include metadata about strategies

4. **Context**: Uses strategies from the repository:
   - Stores a reference to the selected strategy
   - Holds a key/identifier for the current strategy type
   - Retrieves strategies from the repository when needed
   - Delegates work to the current strategy

## Implementation Patterns

### Class Registry with Factory Methods

```python
class StrategyRepository:
    _strategies = {}
    
    @classmethod
    def register(cls, key, strategy_class):
        cls._strategies[key] = strategy_class
    
    @classmethod
    def get(cls, key):
        if key not in cls._strategies:
            raise KeyError(f"Strategy '{key}' not found")
        return cls._strategies[key]()
```

### Context with Repository Dependency

```python
class Context:
    def __init__(self, strategy_type):
        self._strategy_type = strategy_type
        self._strategy = StrategyRepository.get(strategy_type)
    
    def execute(self, data):
        return self._strategy.execute(data)
```

## Advantages

1. **Centralized Management**: All available strategies are registered in one place, making the system easier to understand and maintain.

2. **Runtime Registration**: New strategies can be added dynamically at runtime without modifying existing code.

3. **Decoupled Strategy Selection**: The process of selecting a strategy is separated from strategy implementation, allowing for more flexible strategy selection mechanisms.

4. **Configuration-Driven**: Strategy selection can be driven by configuration files, user preferences, or application state.

5. **Metadata Support**: The repository can store additional metadata about strategies, such as descriptions, requirements, or categorization.

6. **Lazy Instantiation**: Strategies can be instantiated only when needed, improving performance for applications with many potential strategies.

## Use Cases

- **Plugin Systems**: When strategies are provided as plugins that can be loaded dynamically.
- **Configuration-Driven Applications**: When the choice of algorithm depends on user settings or configuration files.
- **Feature Toggles**: When different implementations need to be switched based on feature flags.
- **Multi-tenant Systems**: When different tenants need different algorithm implementations.
- **A/B Testing**: When different algorithms need to be tested against each other.

## Detection Approach

The Code Pattern Analyzer identifies repository-based Strategy patterns by looking for:

1. A repository/registry class that:
   - Has a class-level dictionary of strategies
   - Provides registration methods for adding strategies
   - Offers methods to retrieve strategies by key/identifier

2. Context classes that:
   - Store a strategy type/key
   - Retrieve strategies from the repository
   - Delegate work to the retrieved strategy

## Implementation Examples

- See `samples/repository_strategy_sample.py` for a Python implementation
- See `samples/repository_strategy_sample.js` for a JavaScript implementation