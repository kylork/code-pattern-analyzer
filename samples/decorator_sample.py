"""
Sample implementations of the Decorator pattern in Python.

The Decorator pattern allows behavior to be added to individual objects,
either statically or dynamically, without affecting the behavior of other
objects from the same class.
"""

# Implementation 1: Classic Decorator Pattern with Component interface

from abc import ABC, abstractmethod


class Component(ABC):
    """Abstract Component interface."""
    
    @abstractmethod
    def operation(self) -> str:
        """Basic operation that concrete components and decorators implement."""
        pass


class ConcreteComponent(Component):
    """Concrete implementation of the Component interface."""
    
    def operation(self) -> str:
        return "ConcreteComponent"


class Decorator(Component):
    """Base Decorator class that follows the same interface as Component."""
    
    def __init__(self, component: Component):
        """Initialize with the component to be decorated."""
        self._component = component
    
    @property
    def component(self) -> Component:
        """Return the wrapped component."""
        return self._component
    
    def operation(self) -> str:
        """Default behavior is to delegate to the wrapped component."""
        return self._component.operation()


class ConcreteDecoratorA(Decorator):
    """Concrete decorator that adds behavior before/after the component."""
    
    def operation(self) -> str:
        """Add behavior to the component's operation."""
        return f"ConcreteDecoratorA({self.component.operation()})"


class ConcreteDecoratorB(Decorator):
    """Another concrete decorator with additional state and behavior."""
    
    def __init__(self, component: Component):
        """Initialize with component and additional state."""
        super().__init__(component)
        self._additional_state = "Some state"
    
    def operation(self) -> str:
        """Add different behavior to the component's operation."""
        return f"ConcreteDecoratorB({self.component.operation()})"
    
    def additional_behavior(self) -> str:
        """Additional behavior that is not part of the Component interface."""
        return f"Additional behavior: {self._additional_state}"


# Implementation 2: Function Decorators (Python-specific)

def logging_decorator(func):
    """Function decorator that adds logging to a function."""
    
    def wrapper(*args, **kwargs):
        """Wrapper function that adds behavior around the original function."""
        print(f"Calling {func.__name__} with {args}, {kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result
    
    return wrapper


@logging_decorator
def example_function(x, y):
    """Example function that will be decorated with logging."""
    return x + y


# Implementation 3: Class Decorators (Python-specific)

def singleton_decorator(cls):
    """Class decorator that turns a class into a singleton."""
    
    instances = {}
    
    def get_instance(*args, **kwargs):
        """Return the singleton instance of the class."""
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance


@singleton_decorator
class SingletonExample:
    """Example class that will be decorated as a singleton."""
    
    def __init__(self, value=None):
        self.value = value


# Implementation 4: Object composition with explicit decoration

class TextProcessor:
    """Simple text processor that can be decorated."""
    
    def process(self, text: str) -> str:
        """Base processing operation."""
        return text


class UppercaseDecorator:
    """Decorator that adds uppercase functionality."""
    
    def __init__(self, processor):
        """Initialize with the processor to decorate."""
        self.processor = processor
    
    def process(self, text: str) -> str:
        """Process text, then convert to uppercase."""
        return self.processor.process(text).upper()


class BoldDecorator:
    """Decorator that adds bold HTML markup."""
    
    def __init__(self, processor):
        """Initialize with the processor to decorate."""
        self.processor = processor
    
    def process(self, text: str) -> str:
        """Process text, then add bold markup."""
        return f"<b>{self.processor.process(text)}</b>"


# Usage Example
if __name__ == "__main__":
    # Example 1: Classic Decorator Pattern
    print("Example 1: Classic Decorator Pattern")
    simple = ConcreteComponent()
    decorated1 = ConcreteDecoratorA(simple)
    decorated2 = ConcreteDecoratorB(decorated1)
    
    print(f"Simple component: {simple.operation()}")
    print(f"Decorated once: {decorated1.operation()}")
    print(f"Decorated twice: {decorated2.operation()}")
    print(f"Additional behavior: {decorated2.additional_behavior()}")
    
    print("-" * 50)
    
    # Example 2: Function Decorators
    print("Example 2: Function Decorators")
    result = example_function(5, 3)
    print(f"Result: {result}")
    
    print("-" * 50)
    
    # Example 3: Class Decorators
    print("Example 3: Class Decorators")
    singleton1 = SingletonExample("Instance 1")
    singleton2 = SingletonExample("Instance 2")
    print(f"Are instances the same? {singleton1 is singleton2}")
    print(f"Value: {singleton1.value}")  # Still "Instance 1" even though we passed "Instance 2"
    
    print("-" * 50)
    
    # Example 4: Object Composition
    print("Example 4: Object Composition")
    processor = TextProcessor()
    uppercase_processor = UppercaseDecorator(processor)
    bold_uppercase_processor = BoldDecorator(uppercase_processor)
    
    text = "Hello, Decorator Pattern!"
    print(f"Original: {processor.process(text)}")
    print(f"Uppercase: {uppercase_processor.process(text)}")
    print(f"Bold Uppercase: {bold_uppercase_processor.process(text)}")