# Design Pattern Recommendation System

The Pattern Recommendation System analyzes your code to identify opportunities where established design patterns could be applied to improve code quality, maintainability, and flexibility.

## Overview

Unlike pattern detection tools that simply identify existing patterns, this system focuses on detecting code structures that would benefit from refactoring using design patterns. It provides actionable recommendations with:

- Detailed explanations of applicable patterns
- Benefits of applying each pattern
- Code samples showing both current code and suggested implementations
- Confidence scores for each recommendation

## Features

1. **Multiple Pattern Detection**: Identifies opportunities for applying Factory Method, Strategy, Observer, and more patterns
2. **Contextual Recommendations**: Provides pattern suggestions tailored to your specific code context
3. **Code Structure Analysis**: Identifies conditional logic, object creation, and notification code that could be improved
4. **Implementation Guidance**: Includes sample implementations to help you apply patterns correctly
5. **Integration with Code Pattern Analyzer**: Works alongside existing tools to provide a complete analysis

## Pattern Recommendations

The system can currently identify opportunities for applying the following patterns:

### Factory Method Pattern

**What it detects**: Object creation logic inside conditional statements (if-else, switch) that creates different object types based on a condition.

**Benefits**:
- Removes direct dependencies on concrete product classes
- Centralizes object creation logic
- Makes adding new product types easier without modifying existing code
- Promotes the Open/Closed Principle

**Example detection**:
```python
def create_document(file_path):
    extension = file_path.split('.')[-1].lower()
    
    if extension == 'pdf':
        return PDFDocument()
    elif extension == 'docx':
        return WordDocument()
    elif extension == 'txt':
        return TextDocument()
    else:
        raise ValueError(f"Unsupported file type: {extension}")
```

### Strategy Pattern

**What it detects**: Methods with complex conditional logic that select different behaviors based on a condition.

**Benefits**:
- Encapsulates algorithms in separate classes
- Allows easy switching between algorithms at runtime
- Avoids conditional logic in the context class
- Makes adding new strategies possible without changing existing code

**Example detection**:
```python
def calculate_shipping(order_amount, shipping_method, distance_km, weight_kg):
    if shipping_method == "standard":
        # Standard shipping calculation
        base_cost = 5.0
        weight_cost = 0.5 * weight_kg
        distance_cost = 0.1 * distance_km
        return base_cost + weight_cost + distance_cost
        
    elif shipping_method == "express":
        # Express shipping calculation 
        base_cost = 15.0
        weight_cost = 0.8 * weight_kg
        distance_cost = 0.15 * distance_km
        return base_cost + weight_cost + distance_cost
    
    else:
        raise ValueError(f"Unknown shipping method: {shipping_method}")
```

### Observer Pattern

**What it detects**:
- Methods that notify multiple objects about state changes
- Classes that manually maintain lists of listeners/observers
- Code that iterates through collections to notify objects of changes

**Benefits**:
- Establishes a clear one-to-many dependency between objects
- Supports loose coupling between the subject and observers
- Enables dynamic attachment and detachment of observers at runtime
- Encapsulates the notification mechanism

**Example detection**:
```python
def update_order_status(self, order_id, new_status):
    order = self.orders[order_id]
    old_status = order.status
    order.status = new_status
    
    # Notify various components about the status change
    self.notification_service.send_email(...)
    self.analytics_service.track_event(...)
    self.inventory_service.update_inventory(...)
    
    # Notify all listeners
    for listener in self.listeners:
        listener.on_status_changed(order, old_status, new_status)
```

## Usage

You can use the pattern recommendation system in several ways:

### Command Line Tool

The simplest way to get pattern recommendations is with the command-line tool:

```bash
python recommendation_detector.py path/to/file_or_directory
```

This will analyze the code and provide recommendations for pattern applications.

### GUI Interface

For a more user-friendly experience:

```bash
python pattern_recommendation_gui.py
```

This launches a web-based interface where you can:
- Submit code files or directories for analysis
- Browse detailed recommendations with code examples
- View implementation suggestions
- Save reports for later reference

### Integration with Code Pattern Analyzer

The pattern recommendation system integrates with the main Code Pattern Analyzer, providing a complete solution for analyzing and improving your code architecture:

```bash
python integrate_pattern_recommendations.py --run-gui
```

## How It Works

The system uses a combination of techniques to identify pattern opportunities:

1. **Regular Expression Analysis**: Identifies common code structures that match specific patterns
2. **AST Analysis**: Examines the abstract syntax tree of your code to find more complex patterns
3. **Heuristic Evaluation**: Uses heuristics to determine the confidence level of each recommendation
4. **Pattern-Specific Detectors**: Custom detectors for each supported design pattern

## Next Steps

To enhance your code with the identified pattern opportunities:

1. Review the recommendations and assess which ones provide the most value
2. Study the sample implementations provided
3. Apply the patterns gradually, starting with high-confidence recommendations
4. Run tests after each refactoring to ensure behavior hasn't changed
5. Re-run the analyzer to verify the issues have been resolved