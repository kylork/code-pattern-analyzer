#!/usr/bin/env python3
"""
Pattern Transformer

This module provides functionality to automatically transform code that presents
opportunities for design patterns into proper implementations of those patterns.

Usage:
    python pattern_transformer.py --input file_to_transform.py --pattern "Factory Method" --output transformed.py
"""

import os
import sys
import re
import ast
import argparse
import logging
import importlib.util
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Set, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Import the recommendation detector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recommendation_detector import detect_pattern_opportunities, DETECTORS

class CodeTransformer:
    """Base class for code transformers."""
    
    def __init__(self, file_path: str, opportunities: List[Dict]):
        self.file_path = file_path
        self.opportunities = opportunities
        
        # Read the original code
        with open(file_path, 'r', encoding='utf-8') as f:
            self.original_code = f.read()
        
        self.transformed_code = self.original_code
    
    def transform(self) -> str:
        """Transform the code to apply the pattern."""
        raise NotImplementedError("Subclasses must implement transform()")
    
    def save(self, output_path: str) -> None:
        """Save the transformed code to a file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.transformed_code)

class FactoryMethodTransformer(CodeTransformer):
    """Transformer for Factory Method pattern."""
    
    def transform(self) -> str:
        """Transform the code to apply the Factory Method pattern."""
        # Parse the original code
        tree = ast.parse(self.original_code)
        
        # Identify classes and function that will be transformed
        classes = {}
        factory_function = None
        
        # Find all class definitions
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes[node.name] = node
            
            # Look for the factory function (from opportunities)
            if isinstance(node, ast.FunctionDef):
                for opportunity in self.opportunities:
                    if opportunity["pattern_name"] == "Factory Method":
                        # Extract the line range
                        start_line, end_line = opportunity["line_range"]
                        
                        # Check if this function contains the opportunity
                        if node.lineno <= start_line and node.end_lineno >= end_line:
                            factory_function = node
                            break
        
        if not factory_function:
            logger.warning("No factory function found in opportunities")
            return self.original_code
        
        # Extract created classes from the factory function
        created_classes = set()
        for node in ast.walk(factory_function):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in classes:
                    created_classes.add(node.func.id)
        
        if not created_classes:
            logger.warning("No created classes found in factory function")
            return self.original_code
        
        # Find the common base class or interface
        # For now, we'll assume all classes have common methods
        common_methods = None
        for class_name in created_classes:
            class_node = classes[class_name]
            
            # Get all method names in this class
            methods = set()
            for node in class_node.body:
                if isinstance(node, ast.FunctionDef) and not node.name.startswith('__'):
                    methods.add(node.name)
            
            if common_methods is None:
                common_methods = methods
            else:
                common_methods &= methods
        
        if not common_methods:
            logger.warning("No common methods found in created classes")
            common_methods = set()
        
        # Generate the transformed code
        transformed_lines = self.original_code.splitlines()
        
        # Find insertion point for the abstract class (before the first concrete class)
        first_class_line = min(classes[class_name].lineno for class_name in created_classes) - 1
        
        # Generate the abstract product class
        product_class_lines = [
            "from abc import ABC, abstractmethod",
            "",
            "# Abstract Product",
            "class Product(ABC):"
        ]
        
        for method in sorted(common_methods):
            product_class_lines.append(f"    @abstractmethod")
            product_class_lines.append(f"    def {method}(self):")
            product_class_lines.append(f"        pass")
            product_class_lines.append(f"")
        
        # Update concrete classes to inherit from Product
        concrete_class_changes = {}
        for class_name in created_classes:
            class_node = classes[class_name]
            class_line = transformed_lines[class_node.lineno - 1]
            
            # Update class definition to inherit from Product
            if "(" in class_line:
                # Already has inheritance
                new_class_line = class_line.replace("(", "(Product, ")
            else:
                # No inheritance yet
                new_class_line = class_line.replace(":", "(Product):")
            
            concrete_class_changes[class_node.lineno - 1] = new_class_line
        
        # Create factory interface
        factory_method_name = factory_function.name
        factory_class_lines = [
            "",
            "# Creator (Factory) interface",
            "class Creator(ABC):",
            f"    @abstractmethod",
            f"    def {factory_method_name}(self):",
            f"        pass",
            ""
        ]
        
        # Create concrete factory implementations
        concrete_factories = []
        for class_name in created_classes:
            factory_name = f"{class_name}Creator"
            concrete_factories.append(factory_name)
            factory_class_lines.extend([
                f"# Concrete Creator for {class_name}",
                f"class {factory_name}(Creator):",
                f"    def {factory_method_name}(self):",
                f"        return {class_name}()",
                ""
            ])
        
        # Generate client code example
        client_code = [
            "",
            "# Client code example",
            "def client_code(creator: Creator):",
            f"    # Use the factory method to create a product",
            f"    product = creator.{factory_method_name}()",
            f"    # Use the product",
            f"    return product",
            "",
            "# Usage example",
            "if __name__ == '__main__':"
        ]
        
        for factory in concrete_factories:
            client_code.append(f"    # Create and use a {factory}")
            client_code.append(f"    creator = {factory}()")
            client_code.append(f"    product = client_code(creator)")
            client_code.append(f"    print(product)")
            client_code.append(f"")
        
        # Insert all the new code
        # First, insert the abstract product class
        for i, line in enumerate(product_class_lines):
            transformed_lines.insert(first_class_line + i, line)
        
        # Update the insertion point for the next additions
        insertion_offset = len(product_class_lines)
        
        # Update concrete classes to inherit from Product
        for line_num, new_line in concrete_class_changes.items():
            transformed_lines[line_num + insertion_offset] = new_line
        
        # Find the factory function
        factory_line = factory_function.lineno - 1 + insertion_offset
        factory_end_line = factory_function.end_lineno + insertion_offset
        
        # Insert the factory classes after the original factory function
        for i, line in enumerate(factory_class_lines):
            transformed_lines.insert(factory_end_line + i, line)
        
        # Update insertion point for client code
        insertion_offset += len(factory_class_lines)
        
        # Find the end of the file or main block
        if "__main__" in self.original_code:
            # Find the main block to replace
            main_start = None
            for i, line in enumerate(transformed_lines):
                if "if __name__ == '__main__':" in line:
                    main_start = i
                    break
            
            if main_start is not None:
                # Replace the main block
                transformed_lines = transformed_lines[:main_start] + client_code
            else:
                # Add to the end
                transformed_lines.extend(client_code)
        else:
            # Add to the end
            transformed_lines.extend(client_code)
        
        # Return the transformed code
        self.transformed_code = "\n".join(transformed_lines)
        return self.transformed_code

class StrategyTransformer(CodeTransformer):
    """Transformer for Strategy pattern."""
    
    def transform(self) -> str:
        """Transform the code to apply the Strategy pattern."""
        # Parse the original code
        tree = ast.parse(self.original_code)
        
        # Identify the method containing the strategy
        strategy_method = None
        
        # Look for the strategy method (from opportunities)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for opportunity in self.opportunities:
                    if opportunity["pattern_name"] == "Strategy":
                        # Extract the line range
                        start_line, end_line = opportunity["line_range"]
                        
                        # Check if this function contains the opportunity
                        if node.lineno <= start_line and node.end_lineno >= end_line:
                            strategy_method = node
                            break
        
        if not strategy_method:
            logger.warning("No strategy method found in opportunities")
            return self.original_code
        
        # Extract method details
        method_name = strategy_method.name
        
        # Find the condition variable
        condition_var = None
        for node in ast.walk(strategy_method):
            if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
                if isinstance(node.test.left, ast.Name):
                    condition_var = node.test.left.id
                    break
        
        if not condition_var:
            logger.warning("No condition variable found in strategy method")
            # Try to find any condition variable
            for node in ast.walk(strategy_method):
                if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
                    # Try to extract a condition variable using string representation
                    condition_str = ast.unparse(node.test)
                    condition_parts = condition_str.split()
                    if len(condition_parts) > 0:
                        condition_var = condition_parts[0]
                        break
        
        if not condition_var:
            logger.warning("Could not determine condition variable")
            condition_var = "strategy_type"  # Default fallback
        
        # Find all return statements to determine the strategy behaviors
        behaviors = []
        strategy_blocks = {}
        
        # Walk through the function to find conditionals with return statements
        for node in ast.walk(strategy_method):
            if isinstance(node, ast.If):
                # Extract the condition
                condition = ast.unparse(node.test)
                
                # Find return statements in the body
                body_returns = []
                for body_node in ast.walk(node):
                    if isinstance(body_node, ast.Return):
                        body_returns.append(body_node)
                
                if body_returns:
                    strategy_name = f"Strategy_{len(behaviors) + 1}"
                    
                    # Try to extract a more meaningful name from the condition
                    if condition_var in condition:
                        # Extract the right side of the condition
                        condition_parts = condition.split("==")
                        if len(condition_parts) > 1:
                            # Take the right side, strip quotes and whitespace
                            strategy_value = condition_parts[1].strip().strip('"\'')
                            # Convert to CamelCase
                            strategy_name = "".join(word.capitalize() for word in strategy_value.split("_"))
                            strategy_name += "Strategy"
                    
                    # Get the code block for this strategy
                    strategy_lines = []
                    for i in range(node.lineno, node.end_lineno + 1):
                        strategy_lines.append(self.original_code.splitlines()[i - 1])
                    
                    strategy_blocks[strategy_name] = {
                        "condition": condition,
                        "code": "\n".join(strategy_lines),
                        "returns": [ast.unparse(ret) for ret in body_returns]
                    }
                    
                    behaviors.append(strategy_name)
        
        if not behaviors:
            logger.warning("No strategy behaviors found in method")
            return self.original_code
        
        # Extract the method parameters
        method_params = []
        for arg in strategy_method.args.args:
            if arg.arg != 'self':
                method_params.append(arg.arg)
        
        # Generate the transformed code
        transformed_lines = self.original_code.splitlines()
        
        # Find insertion point (before the class or function containing the strategy method)
        containing_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for subnode in node.body:
                    if isinstance(subnode, ast.FunctionDef) and subnode.name == method_name:
                        containing_class = node
                        break
        
        insertion_point = 1
        if containing_class:
            insertion_point = containing_class.lineno - 1
        else:
            insertion_point = strategy_method.lineno - 1
        
        # Generate the Strategy interface and implementations
        strategy_classes = [
            "from abc import ABC, abstractmethod",
            "",
            "# Strategy interface",
            f"class {method_name.capitalize()}Strategy(ABC):",
            f"    @abstractmethod",
            f"    def execute({', '.join(['self'] + method_params)}):",
            f"        pass",
            ""
        ]
        
        # Generate concrete strategies
        for strategy_name in behaviors:
            block = strategy_blocks[strategy_name]
            
            strategy_classes.extend([
                f"# Concrete strategy for {strategy_name}",
                f"class {strategy_name}({method_name.capitalize()}Strategy):",
                f"    def execute({', '.join(['self'] + method_params)}):",
            ])
            
            # Extract the strategy implementation
            # We'll use a return statement from the original code
            if block["returns"]:
                return_statement = block["returns"][0]
                # Remove 'return ' from the start
                if return_statement.startswith("return "):
                    return_statement = return_statement[7:]
                
                strategy_classes.append(f"        return {return_statement}")
            else:
                strategy_classes.append(f"        pass  # Implementation needed")
            
            strategy_classes.append("")
        
        # Generate the Context class
        context_classes = [
            "# Context class",
            f"class {method_name.capitalize()}Context:",
            f"    def __init__(self, strategy: {method_name.capitalize()}Strategy = None):",
            f"        self._strategy = strategy",
            "",
            f"    def set_strategy(self, strategy: {method_name.capitalize()}Strategy):",
            f"        self._strategy = strategy",
            "",
            f"    def execute_strategy({', '.join(['self'] + method_params)}):",
            f"        if self._strategy is None:",
            f"            raise ValueError(\"Strategy not set\")",
            f"        return self._strategy.execute({', '.join(method_params)})",
            ""
        ]
        
        # Generate factory method to create strategies based on the original condition
        factory_method = [
            f"# Factory method to create strategies based on {condition_var}",
            f"def create_{method_name}_strategy({condition_var}):",
        ]
        
        for strategy_name in behaviors:
            block = strategy_blocks[strategy_name]
            # Extract the condition, assuming it's in the form "x == y"
            # This is a simplification - proper parsing would be more complex
            condition = block["condition"]
            
            # Check if the condition contains the condition variable
            if condition_var in condition:
                # Try to extract the comparison value
                condition_parts = condition.split("==")
                if len(condition_parts) > 1:
                    comparison_value = condition_parts[1].strip()
                    factory_method.append(f"    if {condition_var} == {comparison_value}:")
                    factory_method.append(f"        return {strategy_name}()")
                else:
                    # Fallback
                    factory_method.append(f"    if {condition}:")
                    factory_method.append(f"        return {strategy_name}()")
            else:
                # Fallback
                factory_method.append(f"    if {condition}:")
                factory_method.append(f"        return {strategy_name}()")
        
        # Add a default case
        factory_method.append(f"    raise ValueError(f\"Unknown strategy type: {{{condition_var}}}\")")
        factory_method.append("")
        
        # Generate client code example
        client_code = [
            "",
            "# Client code example",
            "def client_code():",
            f"    # Create a context",
            f"    context = {method_name.capitalize()}Context()",
            "",
            f"    # Set different strategies",
        ]
        
        # Add examples for each strategy
        for strategy_name in behaviors:
            client_code.append(f"    # Use {strategy_name}")
            client_code.append(f"    context.set_strategy({strategy_name}())")
            client_code.append(f"    result = context.execute_strategy({', '.join(['value' for _ in method_params])})")
            client_code.append(f"    print(f\"{strategy_name} result: {{result}}\")")
            client_code.append(f"")
        
        client_code.extend([
            f"    # Alternatively, use the factory method",
            f"    for strategy_type in [{', '.join([repr(s) for s in behaviors])}]:",
            f"        strategy = create_{method_name}_strategy(strategy_type)",
            f"        context.set_strategy(strategy)",
            f"        result = context.execute_strategy({', '.join(['value' for _ in method_params])})",
            f"        print(f\"{{strategy_type}} result: {{result}}\")",
            "",
            "# Usage example",
            "if __name__ == '__main__':",
            "    client_code()",
        ])
        
        # Insert all the new code
        # First, insert the strategy classes
        for i, line in enumerate(strategy_classes):
            transformed_lines.insert(insertion_point + i, line)
        
        # Update the insertion point
        insertion_point += len(strategy_classes)
        
        # Insert the context classes
        for i, line in enumerate(context_classes):
            transformed_lines.insert(insertion_point + i, line)
        
        # Update the insertion point
        insertion_point += len(context_classes)
        
        # Insert the factory method
        for i, line in enumerate(factory_method):
            transformed_lines.insert(insertion_point + i, line)
        
        # Find the end of the file or main block
        if "__main__" in self.original_code:
            # Find the main block to replace
            main_start = None
            for i, line in enumerate(transformed_lines):
                if "if __name__ == '__main__':" in line:
                    main_start = i
                    break
            
            if main_start is not None:
                # Replace the main block
                transformed_lines = transformed_lines[:main_start] + client_code
            else:
                # Add to the end
                transformed_lines.extend(client_code)
        else:
            # Add to the end
            transformed_lines.extend(client_code)
        
        # Return the transformed code
        self.transformed_code = "\n".join(transformed_lines)
        return self.transformed_code

class ObserverTransformer(CodeTransformer):
    """Transformer for Observer pattern."""
    
    def transform(self) -> str:
        """Transform the code to apply the Observer pattern."""
        # Parse the original code
        tree = ast.parse(self.original_code)
        
        # Identify classes and methods using observer-like behavior
        subject_class = None
        notification_methods = []
        
        # Find the class containing notification methods
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if this class contains any of the notification methods from opportunities
                for opportunity in self.opportunities:
                    if opportunity["pattern_name"] == "Observer":
                        # Extract the line range
                        start_line, end_line = opportunity["line_range"]
                        
                        # Check if this class contains the opportunity
                        class_start = node.lineno
                        class_end = node.end_lineno
                        
                        if class_start <= start_line and class_end >= end_line:
                            subject_class = node
                            break
            
            # Look for methods that notify listeners
            if isinstance(node, ast.FunctionDef):
                for opportunity in self.opportunities:
                    if opportunity["pattern_name"] == "Observer":
                        # Extract the line range
                        start_line, end_line = opportunity["line_range"]
                        
                        # Check if this method contains the opportunity
                        method_start = node.lineno
                        method_end = node.end_lineno
                        
                        if method_start <= start_line and method_end >= end_line:
                            notification_methods.append(node)
                            break
        
        if not subject_class:
            logger.warning("No subject class found in opportunities")
            return self.original_code
        
        if not notification_methods:
            logger.warning("No notification methods found in opportunities")
            return self.original_code
        
        # Extract event types from notification methods
        event_types = []
        for method in notification_methods:
            # Look for calls to listener methods
            for node in ast.walk(method):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "listener":
                        event_types.append(node.func.attr)
        
        if not event_types:
            logger.warning("No event types found in notification methods")
            # Use default event types
            event_types = ["update"]
        
        # Remove duplicates
        event_types = list(set(event_types))
        
        # Generate the transformed code
        transformed_lines = self.original_code.splitlines()
        
        # Find insertion point (before the subject class)
        insertion_point = subject_class.lineno - 1
        
        # Generate the Observer interface
        observer_interface = [
            "from abc import ABC, abstractmethod",
            "",
            "# Observer interface",
            "class Observer(ABC):"
        ]
        
        for event_type in event_types:
            # Convert snake_case to camelCase for method names
            method_name = event_type
            if "_" in method_name:
                parts = method_name.split("_")
                method_name = parts[0] + "".join(p.capitalize() for p in parts[1:])
            
            observer_interface.append(f"    @abstractmethod")
            observer_interface.append(f"    def {method_name}(self, *args, **kwargs):")
            observer_interface.append(f"        pass")
            observer_interface.append(f"")
        
        # Generate the Subject interface
        subject_interface = [
            "# Subject interface",
            "class Subject(ABC):",
            "    @abstractmethod",
            "    def attach(self, observer: Observer) -> None:",
            "        pass",
            "",
            "    @abstractmethod",
            "    def detach(self, observer: Observer) -> None:",
            "        pass",
            "",
            "    @abstractmethod",
            "    def notify(self, event_type: str, *args, **kwargs) -> None:",
            "        pass",
            ""
        ]
        
        # Generate the concrete subject implementation
        subject_name = subject_class.name
        concrete_subject = [
            f"# Concrete subject implementation",
            f"class {subject_name}WithObserver({subject_name}, Subject):",
            f"    def __init__(self, *args, **kwargs):",
            f"        super().__init__(*args, **kwargs)",
            f"        self._observers = []",
            f"",
            f"    def attach(self, observer: Observer) -> None:",
            f"        if observer not in self._observers:",
            f"            self._observers.append(observer)",
            f"",
            f"    def detach(self, observer: Observer) -> None:",
            f"        self._observers.remove(observer)",
            f"",
            f"    def notify(self, event_type: str, *args, **kwargs) -> None:",
            f"        for observer in self._observers:",
            f"            # Convert event_type to method name",
            f"            method_name = event_type",
            f"            if '_' in method_name:",
            f"                parts = method_name.split('_')",
            f"                method_name = parts[0] + ''.join(p.capitalize() for p in parts[1:])",
            f"            ",
            f"            if hasattr(observer, method_name) and callable(getattr(observer, method_name)):",
            f"                getattr(observer, method_name)(*args, **kwargs)",
            f""
        ]
        
        # Generate concrete observers
        concrete_observers = []
        for event_type in event_types:
            # Convert snake_case to camelCase for method names
            method_name = event_type
            if "_" in method_name:
                parts = method_name.split("_")
                method_name = parts[0] + "".join(p.capitalize() for p in parts[1:])
            
            # Determine observer name based on event type
            observer_name = "".join(word.capitalize() for word in event_type.split("_"))
            observer_name += "Observer"
            
            concrete_observers.extend([
                f"# Concrete observer for {event_type} events",
                f"class {observer_name}(Observer):"
            ])
            
            # Add implementation for each required method
            for e_type in event_types:
                e_method = e_type
                if "_" in e_method:
                    parts = e_method.split("_")
                    e_method = parts[0] + "".join(p.capitalize() for p in parts[1:])
                
                if e_method == method_name:
                    concrete_observers.extend([
                        f"    def {e_method}(self, *args, **kwargs):",
                        f"        print(f\"{observer_name}: Handling {event_type} event with args={{args}} kwargs={{kwargs}}\")",
                        f"        # Add your custom handling logic here"
                    ])
                else:
                    concrete_observers.extend([
                        f"    def {e_method}(self, *args, **kwargs):",
                        f"        pass  # Not interested in this event"
                    ])
            
            concrete_observers.append("")
        
        # Generate client code example
        client_code = [
            "",
            "# Client code example",
            "def client_code():",
            f"    # Create a subject",
            f"    subject = {subject_name}WithObserver()"
        ]
        
        # Add code for each observer
        for event_type in event_types:
            observer_name = "".join(word.capitalize() for word in event_type.split("_"))
            observer_name += "Observer"
            
            client_code.extend([
                f"    # Create and attach a {observer_name}",
                f"    observer = {observer_name}()",
                f"    subject.attach(observer)"
            ])
        
        client_code.extend([
            f"",
            f"    # Trigger events on the subject",
            f"    # This will automatically notify all attached observers"
        ])
        
        for event_type in event_types:
            if event_type in ["on_order_created", "on_status_changed"]:
                # Use example code from the opportunities
                client_code.extend([
                    f"    # Trigger {event_type} event",
                    f"    order = object()  # This would be a real order object in your code",
                    f"    subject.notify('{event_type}', order)"
                ])
            else:
                client_code.extend([
                    f"    # Trigger {event_type} event",
                    f"    subject.notify('{event_type}', 'example_data')"
                ])
        
        client_code.extend([
            f"",
            f"    # Detach an observer",
            f"    subject.detach(observer)",
            f"",
            f"    # Further events won't notify the detached observer",
            f"    subject.notify('{event_types[0]}', 'this will only notify remaining observers')",
            "",
            "# Usage example",
            "if __name__ == '__main__':",
            "    client_code()",
        ])
        
        # Insert all the new code
        # First, insert the observer and subject interfaces
        all_interfaces = observer_interface + subject_interface
        for i, line in enumerate(all_interfaces):
            transformed_lines.insert(insertion_point + i, line)
        
        # Update the insertion point
        insertion_point += len(all_interfaces)
        
        # Insert the concrete subject implementation after the original subject class
        # Find the end of the original subject class
        subject_end = subject_class.end_lineno
        for i, line in enumerate(concrete_subject):
            transformed_lines.insert(subject_end + i, line)
        
        # Update the insertion point
        insertion_point = subject_end + len(concrete_subject)
        
        # Insert the concrete observers
        for i, line in enumerate(concrete_observers):
            transformed_lines.insert(insertion_point + i, line)
        
        # Find the end of the file or main block
        if "__main__" in self.original_code:
            # Find the main block to replace
            main_start = None
            for i, line in enumerate(transformed_lines):
                if "if __name__ == '__main__':" in line:
                    main_start = i
                    break
            
            if main_start is not None:
                # Replace the main block
                transformed_lines = transformed_lines[:main_start] + client_code
            else:
                # Add to the end
                transformed_lines.extend(client_code)
        else:
            # Add to the end
            transformed_lines.extend(client_code)
        
        # Return the transformed code
        self.transformed_code = "\n".join(transformed_lines)
        return self.transformed_code

def create_transformer(pattern_name: str, file_path: str, opportunities: List[Dict]) -> CodeTransformer:
    """Factory method to create the appropriate transformer based on pattern name."""
    if pattern_name == "Factory Method":
        return FactoryMethodTransformer(file_path, opportunities)
    elif pattern_name == "Strategy":
        return StrategyTransformer(file_path, opportunities)
    elif pattern_name == "Observer":
        return ObserverTransformer(file_path, opportunities)
    else:
        raise ValueError(f"Unsupported pattern: {pattern_name}")

def transform_file(file_path: str, pattern_name: str, output_path: str = None) -> str:
    """Transform a file to apply a design pattern."""
    # Detect pattern opportunities
    opportunities = detect_pattern_opportunities(file_path)
    
    # Filter opportunities by pattern name
    pattern_opportunities = [opp for opp in opportunities if opp["pattern_name"] == pattern_name]
    
    if not pattern_opportunities:
        logger.warning(f"No {pattern_name} pattern opportunities found in {file_path}")
        return None
    
    # Create the transformer
    transformer = create_transformer(pattern_name, file_path, pattern_opportunities)
    
    # Transform the code
    transformed_code = transformer.transform()
    
    # Save the transformed code if output path is provided
    if output_path:
        transformer.save(output_path)
    
    return transformed_code

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Transform code to apply design patterns"
    )
    
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input file to transform"
    )
    
    parser.add_argument(
        "--pattern", "-p",
        required=True,
        choices=["Factory Method", "Strategy", "Observer"],
        help="Design pattern to apply"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file for transformed code (default: input_transformed.py)"
    )
    
    args = parser.parse_args()
    
    # Set default output path if not provided
    if not args.output:
        input_path = Path(args.input)
        args.output = str(input_path.with_stem(f"{input_path.stem}_transformed"))
    
    try:
        # Transform the file
        result = transform_file(args.input, args.pattern, args.output)
        
        if result:
            logger.info(f"Successfully transformed {args.input} to apply {args.pattern} pattern")
            logger.info(f"Transformed code saved to {args.output}")
        else:
            logger.warning(f"Failed to transform {args.input}")
            return 1
    
    except Exception as e:
        logger.error(f"Error transforming file: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())