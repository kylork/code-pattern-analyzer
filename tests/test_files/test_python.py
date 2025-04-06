def simple_function(a, b):
    """A simple function that adds two numbers."""
    return a + b


class SimpleClass:
    """A simple class with methods."""
    
    def __init__(self, value):
        self.value = value
        
    def get_value(self):
        return self.value
        
    def set_value(self, new_value):
        self.value = new_value


def complex_function(a, b, c=None, *args, **kwargs):
    """A more complex function with various parameter types."""
    result = a + b
    
    if c is not None:
        result += c
        
    for arg in args:
        result += arg
        
    for key, value in kwargs.items():
        print(f"{key}: {value}")
        
    return result


class ComplexClass:
    """A more complex class with inheritance and multiple methods."""
    
    class_variable = "I am a class variable"
    
    def __init__(self, value, name):
        self.value = value
        self.name = name
        self._private = 100
        
    @property
    def private(self):
        return self._private
        
    @private.setter
    def private(self, value):
        if value < 0:
            raise ValueError("Private value cannot be negative")
        self._private = value
        
    def calculate(self, multiplier):
        return self.value * multiplier
