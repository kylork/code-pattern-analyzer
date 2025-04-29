"""
Sample implementations of the Adapter pattern in Python.

The Adapter pattern converts the interface of a class into another interface
that clients expect. It allows classes to work together that couldn't otherwise
because of incompatible interfaces.
"""

# Implementation 1: Class Adapter Pattern (using inheritance)
from abc import ABC, abstractmethod


class Target(ABC):
    """Target interface that the client uses."""
    
    @abstractmethod
    def request(self) -> str:
        """Request method that clients call."""
        pass


class Adaptee:
    """Existing class with an incompatible interface."""
    
    def specific_request(self) -> str:
        """Method with a different interface than what clients expect."""
        return "Adaptee's specific behavior"


class Adapter(Target, Adaptee):
    """Adapter that implements the Target interface and inherits from Adaptee."""
    
    def request(self) -> str:
        """Adapt the Adaptee's interface to the Target interface."""
        return f"Adapter: (TRANSLATED) {self.specific_request()}"


# Implementation 2: Object Adapter Pattern (using composition)

class ObjectTarget(ABC):
    """Target interface for object adapter."""
    
    @abstractmethod
    def request(self) -> str:
        """Standard request method."""
        pass


class LegacyService:
    """Legacy service with incompatible interface."""
    
    def legacy_operation(self) -> str:
        """Method with different name and interface."""
        return "Legacy service operation"


class ObjectAdapter(ObjectTarget):
    """Adapter using composition rather than inheritance."""
    
    def __init__(self, adaptee: LegacyService):
        """Initialize with adaptee instance."""
        self.adaptee = adaptee
    
    def request(self) -> str:
        """Adapt the adaptee's interface."""
        return f"ObjectAdapter: {self.adaptee.legacy_operation()}"


# Implementation 3: Function Adapter Pattern

def legacy_function(value: int) -> dict:
    """Legacy function with incompatible return format."""
    return {"result": value * 2, "source": "legacy"}


def adapted_function(value: int) -> int:
    """Adapter function that calls legacy_function but returns a compatible format."""
    result = legacy_function(value)
    return result["result"]


# Implementation 4: Interface Adapter with Multiple Methods

class MultiMethodTarget(ABC):
    """Target interface with multiple methods."""
    
    @abstractmethod
    def method_a(self) -> str:
        """First method."""
        pass
    
    @abstractmethod
    def method_b(self, value: int) -> int:
        """Second method."""
        pass


class ComplexAdaptee:
    """Complex adaptee with different method names and signatures."""
    
    def different_method_a(self) -> str:
        """Method with functionality similar to method_a but different name."""
        return "Complex adaptee behavior A"
    
    def different_method_b(self, val: int, extra: str = "default") -> dict:
        """Method with functionality similar to method_b but different signature."""
        return {"output": val * 3, "extra": extra}


class ComplexAdapter(MultiMethodTarget):
    """Complex adapter that adapts multiple methods."""
    
    def __init__(self, adaptee: ComplexAdaptee):
        """Initialize with complex adaptee."""
        self.adaptee = adaptee
    
    def method_a(self) -> str:
        """Adapt different_method_a to method_a."""
        return f"Adapted A: {self.adaptee.different_method_a()}"
    
    def method_b(self, value: int) -> int:
        """Adapt different_method_b to method_b."""
        result = self.adaptee.different_method_b(value)
        return result["output"]


# Usage Example
if __name__ == "__main__":
    # Example 1: Class Adapter
    print("Example 1: Class Adapter")
    adapter = Adapter()
    print(adapter.request())
    
    print("-" * 50)
    
    # Example 2: Object Adapter
    print("Example 2: Object Adapter")
    legacy_service = LegacyService()
    object_adapter = ObjectAdapter(legacy_service)
    print(object_adapter.request())
    
    print("-" * 50)
    
    # Example 3: Function Adapter
    print("Example 3: Function Adapter")
    print(f"Direct legacy result: {legacy_function(5)}")
    print(f"Adapted result: {adapted_function(5)}")
    
    print("-" * 50)
    
    # Example 4: Complex Interface Adapter
    print("Example 4: Complex Interface Adapter")
    complex_adaptee = ComplexAdaptee()
    complex_adapter = ComplexAdapter(complex_adaptee)
    print(complex_adapter.method_a())
    print(f"Complex adapter method_b: {complex_adapter.method_b(5)}")