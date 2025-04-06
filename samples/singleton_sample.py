"""
Sample implementation of the Singleton pattern in Python.
"""

class Singleton:
    """
    A singleton class implemented using the classic __new__ method.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, value=None):
        # This will be executed multiple times but _instance persists
        if not hasattr(self, 'value'):
            self.value = value or 'Default value'


class SingletonWithInstanceMethod:
    """
    A singleton class implemented using a class method to manage the instance.
    """
    _instance = None
    
    def __init__(self, value=None):
        self.value = value or 'Default value'
    
    @classmethod
    def get_instance(cls, value=None):
        if cls._instance is None:
            cls._instance = cls(value)
        return cls._instance


# Example use of the singleton patterns
singleton1 = Singleton("First")
singleton2 = Singleton("Second")  # This won't change the value

print(f"singleton1.value: {singleton1.value}")
print(f"singleton2.value: {singleton2.value}")
print(f"Are they the same object? {singleton1 is singleton2}")

s1 = SingletonWithInstanceMethod.get_instance("First")
s2 = SingletonWithInstanceMethod.get_instance("Second")  # This won't change the value

print(f"s1.value: {s1.value}")
print(f"s2.value: {s2.value}")
print(f"Are they the same object? {s1 is s2}")

# Bad practice: Using a global for the same effect
_global_instance = None

def get_global_instance(value=None):
    global _global_instance
    if _global_instance is None:
        _global_instance = {'value': value or 'Default value'}
    return _global_instance