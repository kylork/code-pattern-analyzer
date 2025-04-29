"""
A sample Python file for demonstrating the Code Pattern Analyzer.
"""

def greet(name):
    """Greet the user by name."""
    return f"Hello, {name}!"

class Person:
    """Represents a person with a name and age."""
    
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def say_hello(self):
        """Have the person say hello."""
        return f"{self.name} says hello!"
    
    def celebrate_birthday(self):
        """Increment the person's age."""
        self.age += 1
        return f"{self.name} is now {self.age} years old!"

def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

class Calculator:
    """A simple calculator class."""
    
    @staticmethod
    def add(a, b):
        """Add two numbers."""
        return a + b
    
    @staticmethod
    def subtract(a, b):
        """Subtract b from a."""
        return a - b
    
    @staticmethod
    def multiply(a, b):
        """Multiply two numbers."""
        return a * b
    
    @staticmethod
    def divide(a, b):
        """Divide a by b."""
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b