#!/usr/bin/env python3
"""
Pattern Recommendation System

This module analyzes code to identify structures that would benefit from
established design patterns and provides tailored recommendations with
implementation guidance.
"""

import os
import sys
import logging
import re
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Import Code Pattern Analyzer modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.analyzer import analyze_file, analyze_directory
from src.pattern_base import PatternMatch
from src.pattern_registry import get_registered_patterns
from src.parser import parse_file

# Pattern recommendation signatures and templates
class PatternOpportunity:
    """Represents a detected opportunity to apply a design pattern."""
    
    def __init__(
        self,
        pattern_name: str,
        confidence: float,
        file_path: str,
        line_range: Tuple[int, int],
        description: str,
        benefits: List[str],
        code_snippet: str,
        recommended_implementation: str
    ):
        self.pattern_name = pattern_name
        self.confidence = confidence  # 0.0 to 1.0
        self.file_path = file_path
        self.line_range = line_range
        self.description = description
        self.benefits = benefits
        self.code_snippet = code_snippet
        self.recommended_implementation = recommended_implementation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "pattern_name": self.pattern_name,
            "confidence": self.confidence,
            "file_path": self.file_path,
            "line_range": self.line_range,
            "description": self.description,
            "benefits": self.benefits,
            "code_snippet": self.code_snippet,
            "recommended_implementation": self.recommended_implementation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatternOpportunity':
        """Create instance from dictionary."""
        return cls(
            pattern_name=data["pattern_name"],
            confidence=data["confidence"],
            file_path=data["file_path"],
            line_range=tuple(data["line_range"]),
            description=data["description"],
            benefits=data["benefits"],
            code_snippet=data["code_snippet"],
            recommended_implementation=data["recommended_implementation"]
        )
    
    def __str__(self) -> str:
        return f"{self.pattern_name} opportunity (confidence: {self.confidence:.2f}) at {self.file_path}:{self.line_range[0]}-{self.line_range[1]}"

# Registry of opportunity detectors
class OpportunityDetector:
    """Base class for pattern opportunity detectors."""
    
    def __init__(self, pattern_name: str, languages: List[str]):
        self.pattern_name = pattern_name
        self.languages = languages  # Supported languages
    
    def detect(self, file_path: str, code: str, parsed_code: Any) -> List[PatternOpportunity]:
        """Detect opportunities to apply this pattern in the given code."""
        raise NotImplementedError("Subclasses must implement detect()")
    
    def get_benefits(self) -> List[str]:
        """Return the benefits of applying this pattern."""
        raise NotImplementedError("Subclasses must implement get_benefits()")
    
    def get_implementation_template(self, code_context: Dict[str, Any]) -> str:
        """Return a template for implementing this pattern based on the context."""
        raise NotImplementedError("Subclasses must implement get_implementation_template()")
    
    def __str__(self) -> str:
        return f"{self.pattern_name} Detector (supports: {', '.join(self.languages)})"

class FactoryMethodDetector(OpportunityDetector):
    """Detects opportunities to apply the Factory Method pattern."""
    
    def __init__(self):
        super().__init__("Factory Method", ["python", "javascript", "java", "typescript"])
    
    def detect(self, file_path: str, code: str, parsed_code: Any) -> List[PatternOpportunity]:
        """Detect Factory Method opportunities."""
        opportunities = []
        
        # Look for switch statements or if-else chains that create different objects
        switch_patterns = [
            # Python if-else chain creating different objects
            r'if\s+.*?:\s*\n\s+return\s+(\w+)\(\)',
            # Python with multiple if-elif statements creating objects
            r'if\s+.*?:\s*\n\s+return\s+(\w+)\(\).*?elif\s+.*?:\s*\n\s+return\s+(\w+)\(\)',
            # JavaScript/TypeScript switch statements creating objects
            r'switch\s*\([^)]+\)\s*{\s*case[^}]+new\s+\w+\([^)]*\)[^}]+}',
            # Java if-else chains creating objects
            r'if\s*\([^)]+\)\s*{\s*return\s*new\s+\w+\([^)]*\);\s*}\s*else'
        ]
        
        for pattern in switch_patterns:
            matches = re.finditer(pattern, code, re.DOTALL)
            for match in matches:
                start_line = code[:match.start()].count('\n') + 1
                end_line = start_line + code[match.start():match.end()].count('\n')
                
                # Extract the code snippet
                lines = code.splitlines()
                snippet = '\n'.join(lines[start_line-1:end_line])
                
                # Create the opportunity
                opportunity = PatternOpportunity(
                    pattern_name="Factory Method",
                    confidence=0.8,  # High confidence for direct creation patterns
                    file_path=file_path,
                    line_range=(start_line, end_line),
                    description="Object creation logic using conditional statements could be replaced with the Factory Method pattern",
                    benefits=self.get_benefits(),
                    code_snippet=snippet,
                    recommended_implementation=self.get_implementation_template({
                        "snippet": snippet,
                        "language": Path(file_path).suffix[1:]  # Extract language from file extension
                    })
                )
                opportunities.append(opportunity)
        
        return opportunities
    
    def get_benefits(self) -> List[str]:
        return [
            "Removes direct dependencies on concrete product classes",
            "Centralizes object creation logic",
            "Makes adding new product types easier without modifying existing code",
            "Promotes the Open/Closed Principle",
            "Provides hooks for subclasses to customize the factory method"
        ]
    
    def get_implementation_template(self, code_context: Dict[str, Any]) -> str:
        """Generate a Factory Method implementation based on the code context."""
        language = code_context.get("language", "python")
        
        if language == "py":
            return """from abc import ABC, abstractmethod

# Abstract Product
class Product(ABC):
    @abstractmethod
    def operation(self) -> str:
        pass

# Concrete Products
class ConcreteProductA(Product):
    def operation(self) -> str:
        return "Result of ConcreteProductA"

class ConcreteProductB(Product):
    def operation(self) -> str:
        return "Result of ConcreteProductB"

# Creator (Factory)
class Creator(ABC):
    @abstractmethod
    def factory_method(self) -> Product:
        pass
        
    def some_operation(self) -> str:
        # Call the factory method to create a Product object
        product = self.factory_method()
        
        # Now use the product
        return f"Creator: {product.operation()}"

# Concrete Creators
class ConcreteCreatorA(Creator):
    def factory_method(self) -> Product:
        return ConcreteProductA()

class ConcreteCreatorB(Creator):
    def factory_method(self) -> Product:
        return ConcreteProductB()

# Client code
def client_code(creator: Creator) -> None:
    print(f"Client: {creator.some_operation()}")

# Usage
client_code(ConcreteCreatorA())
client_code(ConcreteCreatorB())
"""
        elif language in ["js", "ts"]:
            return """// Abstract Product
interface Product {
    operation(): string;
}

// Concrete Products
class ConcreteProductA implements Product {
    operation(): string {
        return "Result of ConcreteProductA";
    }
}

class ConcreteProductB implements Product {
    operation(): string {
        return "Result of ConcreteProductB";
    }
}

// Creator (Factory)
abstract class Creator {
    // Factory Method
    abstract factoryMethod(): Product;
    
    someOperation(): string {
        // Call the factory method to create a Product object
        const product = this.factoryMethod();
        
        // Now use the product
        return `Creator: ${product.operation()}`;
    }
}

// Concrete Creators
class ConcreteCreatorA extends Creator {
    factoryMethod(): Product {
        return new ConcreteProductA();
    }
}

class ConcreteCreatorB extends Creator {
    factoryMethod(): Product {
        return new ConcreteProductB();
    }
}

// Client code
function clientCode(creator: Creator) {
    console.log(`Client: ${creator.someOperation()}`);
}

// Usage
clientCode(new ConcreteCreatorA());
clientCode(new ConcreteCreatorB());
"""
        elif language == "java":
            return """// Abstract Product
interface Product {
    String operation();
}

// Concrete Products
class ConcreteProductA implements Product {
    @Override
    public String operation() {
        return "Result of ConcreteProductA";
    }
}

class ConcreteProductB implements Product {
    @Override
    public String operation() {
        return "Result of ConcreteProductB";
    }
}

// Creator (Factory)
abstract class Creator {
    // Factory Method
    public abstract Product factoryMethod();
    
    public String someOperation() {
        // Call the factory method to create a Product object
        Product product = factoryMethod();
        
        // Now use the product
        return "Creator: " + product.operation();
    }
}

// Concrete Creators
class ConcreteCreatorA extends Creator {
    @Override
    public Product factoryMethod() {
        return new ConcreteProductA();
    }
}

class ConcreteCreatorB extends Creator {
    @Override
    public Product factoryMethod() {
        return new ConcreteProductB();
    }
}

// Client code
class Client {
    public static void clientCode(Creator creator) {
        System.out.println("Client: " + creator.someOperation());
    }
    
    public static void main(String[] args) {
        clientCode(new ConcreteCreatorA());
        clientCode(new ConcreteCreatorB());
    }
}
"""
        else:
            return "// Implementation template for this language is not available yet."

class StrategyDetector(OpportunityDetector):
    """Detects opportunities to apply the Strategy pattern."""
    
    def __init__(self):
        super().__init__("Strategy", ["python", "javascript", "java", "typescript"])
    
    def detect(self, file_path: str, code: str, parsed_code: Any) -> List[PatternOpportunity]:
        """Detect Strategy pattern opportunities."""
        opportunities = []
        
        # Look for switch/if-else statements that select a behavior based on a condition
        behavior_switch_patterns = [
            # Python if-else chain selecting behavior
            r'if\s+.*?:\s*\n\s+.*?\n\s+.*?\n\s+elif\s+.*?:\s*\n\s+.*?\n\s+.*?\n\s+else',
            # Method with multiple conditional branches performing similar operations
            r'def\s+\w+\([^)]*\):\s*\n(?:\s+if\s+.*?:\s*\n\s+.*?\n){2,}',
            # JavaScript/TypeScript switch with multiple cases
            r'switch\s*\([^)]+\)\s*{\s*case[^:]+:[^;]+;[^}]+case[^:]+:[^;]+;[^}]+}',
            # Java if-else chains
            r'if\s*\([^)]+\)\s*{\s*[^}]+\s*}\s*else\s+if\s*\([^)]+\)\s*{\s*[^}]+\s*}\s*else\s*{'
        ]
        
        for pattern in behavior_switch_patterns:
            matches = re.finditer(pattern, code, re.DOTALL)
            for match in matches:
                start_line = code[:match.start()].count('\n') + 1
                end_line = start_line + code[match.start():match.end()].count('\n')
                
                # Extract the code snippet
                lines = code.splitlines()
                snippet = '\n'.join(lines[start_line-1:end_line])
                
                # Create the opportunity
                opportunity = PatternOpportunity(
                    pattern_name="Strategy",
                    confidence=0.7,  # Medium-high confidence for behavior switching patterns
                    file_path=file_path,
                    line_range=(start_line, end_line),
                    description="Conditional logic selecting different behaviors could be replaced with the Strategy pattern",
                    benefits=self.get_benefits(),
                    code_snippet=snippet,
                    recommended_implementation=self.get_implementation_template({
                        "snippet": snippet,
                        "language": Path(file_path).suffix[1:]  # Extract language from file extension
                    })
                )
                opportunities.append(opportunity)
        
        return opportunities
    
    def get_benefits(self) -> List[str]:
        return [
            "Encapsulates algorithms in separate classes",
            "Allows easy switching between algorithms at runtime",
            "Avoids conditional logic in the context class",
            "Makes adding new strategies possible without changing existing code",
            "Promotes the Open/Closed Principle",
            "Isolates algorithm-specific code, improving maintainability"
        ]
    
    def get_implementation_template(self, code_context: Dict[str, Any]) -> str:
        """Generate a Strategy implementation based on the code context."""
        language = code_context.get("language", "python")
        
        if language == "py":
            return """from abc import ABC, abstractmethod

# Strategy interface
class Strategy(ABC):
    @abstractmethod
    def execute(self, data):
        pass

# Concrete strategies
class ConcreteStrategyA(Strategy):
    def execute(self, data):
        return f"Strategy A applied to {data}"

class ConcreteStrategyB(Strategy):
    def execute(self, data):
        return f"Strategy B applied to {data}"

class ConcreteStrategyC(Strategy):
    def execute(self, data):
        return f"Strategy C applied to {data}"

# Context class
class Context:
    def __init__(self, strategy: Strategy = None):
        self._strategy = strategy
    
    @property
    def strategy(self) -> Strategy:
        return self._strategy
    
    @strategy.setter
    def strategy(self, strategy: Strategy):
        self._strategy = strategy
    
    def execute_strategy(self, data):
        if not self._strategy:
            raise ValueError("Strategy not set")
        return self._strategy.execute(data)

# Client code
if __name__ == "__main__":
    # Create context with an initial strategy
    context = Context(ConcreteStrategyA())
    print(context.execute_strategy("sample data"))
    
    # Change strategy at runtime
    context.strategy = ConcreteStrategyB()
    print(context.execute_strategy("sample data"))
    
    context.strategy = ConcreteStrategyC()
    print(context.execute_strategy("sample data"))
"""
        elif language in ["js", "ts"]:
            return """// Strategy interface
interface Strategy {
    execute(data: string): string;
}

// Concrete strategies
class ConcreteStrategyA implements Strategy {
    execute(data: string): string {
        return `Strategy A applied to ${data}`;
    }
}

class ConcreteStrategyB implements Strategy {
    execute(data: string): string {
        return `Strategy B applied to ${data}`;
    }
}

class ConcreteStrategyC implements Strategy {
    execute(data: string): string {
        return `Strategy C applied to ${data}`;
    }
}

// Context class
class Context {
    private strategy: Strategy | null = null;
    
    constructor(strategy?: Strategy) {
        if (strategy) {
            this.strategy = strategy;
        }
    }
    
    setStrategy(strategy: Strategy): void {
        this.strategy = strategy;
    }
    
    executeStrategy(data: string): string {
        if (!this.strategy) {
            throw new Error("Strategy not set");
        }
        return this.strategy.execute(data);
    }
}

// Client code
const context = new Context(new ConcreteStrategyA());
console.log(context.executeStrategy("sample data"));

// Change strategy at runtime
context.setStrategy(new ConcreteStrategyB());
console.log(context.executeStrategy("sample data"));

context.setStrategy(new ConcreteStrategyC());
console.log(context.executeStrategy("sample data"));
"""
        elif language == "java":
            return """// Strategy interface
interface Strategy {
    String execute(String data);
}

// Concrete strategies
class ConcreteStrategyA implements Strategy {
    @Override
    public String execute(String data) {
        return "Strategy A applied to " + data;
    }
}

class ConcreteStrategyB implements Strategy {
    @Override
    public String execute(String data) {
        return "Strategy B applied to " + data;
    }
}

class ConcreteStrategyC implements Strategy {
    @Override
    public String execute(String data) {
        return "Strategy C applied to " + data;
    }
}

// Context class
class Context {
    private Strategy strategy;
    
    public Context() {
        this.strategy = null;
    }
    
    public Context(Strategy strategy) {
        this.strategy = strategy;
    }
    
    public void setStrategy(Strategy strategy) {
        this.strategy = strategy;
    }
    
    public String executeStrategy(String data) {
        if (strategy == null) {
            throw new IllegalStateException("Strategy not set");
        }
        return strategy.execute(data);
    }
}

// Client code
class StrategyDemo {
    public static void main(String[] args) {
        Context context = new Context(new ConcreteStrategyA());
        System.out.println(context.executeStrategy("sample data"));
        
        // Change strategy at runtime
        context.setStrategy(new ConcreteStrategyB());
        System.out.println(context.executeStrategy("sample data"));
        
        context.setStrategy(new ConcreteStrategyC());
        System.out.println(context.executeStrategy("sample data"));
    }
}
"""
        else:
            return "// Implementation template for this language is not available yet."

class ObserverDetector(OpportunityDetector):
    """Detects opportunities to apply the Observer pattern."""
    
    def __init__(self):
        super().__init__("Observer", ["python", "javascript", "java", "typescript"])
    
    def detect(self, file_path: str, code: str, parsed_code: Any) -> List[PatternOpportunity]:
        """Detect Observer pattern opportunities."""
        opportunities = []
        
        # Look for code that manually updates multiple dependent objects
        notification_patterns = [
            # Methods that call notification/update methods on multiple objects
            r'def\s+\w+\([^)]*\):\s*\n(?:\s+.*?update\(.*?\)\s*\n)+',
            r'def\s+\w+\([^)]*\):\s*\n(?:\s+.*?notify\(.*?\)\s*\n)+',
            r'def\s+\w+\([^)]*\):\s*\n(?:\s+.*?on_change\(.*?\)\s*\n)+',
            # Methods that iterate over a list and notify each element
            r'for\s+\w+\s+in\s+\w+:\s*\n\s+\w+\.(?:update|notify|on_change)\(',
            # JavaScript/TypeScript notification patterns
            r'function\s+\w+\([^)]*\)\s*{\s*(?:.*?\.update\(.*?\);)+',
            r'(?:this|self)\.(?:observers|listeners)\.forEach\(',
            # Java notification patterns
            r'for\s*\([^)]+\s+\w+\s*:\s*\w+\)\s*{\s*\w+\.(?:update|notify|onChange)\('
        ]
        
        for pattern in notification_patterns:
            matches = re.finditer(pattern, code, re.DOTALL)
            for match in matches:
                start_line = code[:match.start()].count('\n') + 1
                end_line = start_line + code[match.start():match.end()].count('\n')
                
                # Extract the code snippet
                lines = code.splitlines()
                snippet = '\n'.join(lines[start_line-1:end_line])
                
                # Create the opportunity
                opportunity = PatternOpportunity(
                    pattern_name="Observer",
                    confidence=0.85,  # High confidence for notification patterns
                    file_path=file_path,
                    line_range=(start_line, end_line),
                    description="Code that notifies multiple objects of changes could be refactored using the Observer pattern",
                    benefits=self.get_benefits(),
                    code_snippet=snippet,
                    recommended_implementation=self.get_implementation_template({
                        "snippet": snippet,
                        "language": Path(file_path).suffix[1:]  # Extract language from file extension
                    })
                )
                opportunities.append(opportunity)
        
        return opportunities
    
    def get_benefits(self) -> List[str]:
        return [
            "Establishes a clear one-to-many dependency between objects",
            "Supports loose coupling between the subject and observers",
            "Enables dynamic attachment and detachment of observers at runtime",
            "Encapsulates the notification mechanism",
            "Eliminates the need to maintain manual lists of dependent objects",
            "Easily extensible to add new observer types without modifying the subject"
        ]
    
    def get_implementation_template(self, code_context: Dict[str, Any]) -> str:
        """Generate an Observer implementation based on the code context."""
        language = code_context.get("language", "python")
        
        if language == "py":
            return """from abc import ABC, abstractmethod
from typing import List

# Observer interface
class Observer(ABC):
    @abstractmethod
    def update(self, subject):
        pass

# Subject (Observable)
class Subject:
    def __init__(self):
        self._observers: List[Observer] = []
        self._state = None
    
    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)
    
    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self)
    
    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, state):
        self._state = state
        self.notify()

# Concrete Observers
class ConcreteObserverA(Observer):
    def update(self, subject: Subject) -> None:
        print(f"ConcreteObserverA: Reacted to state change: {subject.state}")

class ConcreteObserverB(Observer):
    def update(self, subject: Subject) -> None:
        print(f"ConcreteObserverB: Reacted to state change: {subject.state}")

# Client code
if __name__ == "__main__":
    # Create Subject and Observers
    subject = Subject()
    observer_a = ConcreteObserverA()
    observer_b = ConcreteObserverB()
    
    # Register observers
    subject.attach(observer_a)
    subject.attach(observer_b)
    
    # Change state - observers will be notified
    subject.state = "State 1"
    
    # Detach one observer
    subject.detach(observer_a)
    
    # Change state again - only remaining observers will be notified
    subject.state = "State 2"
"""
        elif language in ["js", "ts"]:
            return """// Observer interface
interface Observer {
    update(subject: Subject): void;
}

// Subject (Observable)
class Subject {
    private observers: Observer[] = [];
    private _state: any = null;
    
    public attach(observer: Observer): void {
        const isExist = this.observers.includes(observer);
        if (!isExist) {
            this.observers.push(observer);
        }
    }
    
    public detach(observer: Observer): void {
        const observerIndex = this.observers.indexOf(observer);
        if (observerIndex !== -1) {
            this.observers.splice(observerIndex, 1);
        }
    }
    
    public notify(): void {
        for (const observer of this.observers) {
            observer.update(this);
        }
    }
    
    public get state(): any {
        return this._state;
    }
    
    public set state(value: any) {
        this._state = value;
        this.notify();
    }
}

// Concrete Observers
class ConcreteObserverA implements Observer {
    public update(subject: Subject): void {
        console.log(`ConcreteObserverA: Reacted to state change: ${subject.state}`);
    }
}

class ConcreteObserverB implements Observer {
    public update(subject: Subject): void {
        console.log(`ConcreteObserverB: Reacted to state change: ${subject.state}`);
    }
}

// Client code
const subject = new Subject();
const observerA = new ConcreteObserverA();
const observerB = new ConcreteObserverB();

// Register observers
subject.attach(observerA);
subject.attach(observerB);

// Change state - observers will be notified
subject.state = "State 1";

// Detach one observer
subject.detach(observerA);

// Change state again - only remaining observers will be notified
subject.state = "State 2";
"""
        elif language == "java":
            return """import java.util.ArrayList;
import java.util.List;

// Observer interface
interface Observer {
    void update(Subject subject);
}

// Subject (Observable)
class Subject {
    private final List<Observer> observers = new ArrayList<>();
    private Object state;
    
    public void attach(Observer observer) {
        if (!observers.contains(observer)) {
            observers.add(observer);
        }
    }
    
    public void detach(Observer observer) {
        observers.remove(observer);
    }
    
    public void notify() {
        for (Observer observer : observers) {
            observer.update(this);
        }
    }
    
    public Object getState() {
        return state;
    }
    
    public void setState(Object state) {
        this.state = state;
        notify();
    }
}

// Concrete Observers
class ConcreteObserverA implements Observer {
    @Override
    public void update(Subject subject) {
        System.out.println("ConcreteObserverA: Reacted to state change: " + subject.getState());
    }
}

class ConcreteObserverB implements Observer {
    @Override
    public void update(Subject subject) {
        System.out.println("ConcreteObserverB: Reacted to state change: " + subject.getState());
    }
}

// Client code
class ObserverDemo {
    public static void main(String[] args) {
        // Create Subject and Observers
        Subject subject = new Subject();
        Observer observerA = new ConcreteObserverA();
        Observer observerB = new ConcreteObserverB();
        
        // Register observers
        subject.attach(observerA);
        subject.attach(observerB);
        
        // Change state - observers will be notified
        subject.setState("State 1");
        
        // Detach one observer
        subject.detach(observerA);
        
        // Change state again - only remaining observers will be notified
        subject.setState("State 2");
    }
}
"""
        else:
            return "// Implementation template for this language is not available yet."

# Registry of all opportunity detectors
OPPORTUNITY_DETECTORS = [
    FactoryMethodDetector(),
    StrategyDetector(),
    ObserverDetector()
]

def detect_opportunities(file_path: str) -> List[PatternOpportunity]:
    """Detect pattern opportunities in a single file."""
    # Check if file exists
    if not os.path.isfile(file_path):
        logger.error(f"File does not exist: {file_path}")
        return []
    
    # Read file content
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    
    # Get file language
    language = Path(file_path).suffix[1:]  # Extract language from file extension
    
    # Parse the code
    parsed_code = parse_file(file_path)
    
    opportunities = []
    
    # Run all detectors that support this language
    for detector in OPPORTUNITY_DETECTORS:
        if language in detector.languages:
            try:
                file_opportunities = detector.detect(file_path, code, parsed_code)
                opportunities.extend(file_opportunities)
            except Exception as e:
                logger.error(f"Error in {detector.pattern_name} detector: {str(e)}")
    
    return opportunities

def analyze_directory_for_opportunities(directory_path: str) -> Dict[str, List[PatternOpportunity]]:
    """Analyze a directory for pattern opportunities."""
    results = {}
    
    # Walk through directory
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            # Skip non-source files
            if not file.endswith(('.py', '.js', '.ts', '.java')):
                continue
                
            file_path = os.path.join(root, file)
            opportunities = detect_opportunities(file_path)
            
            if opportunities:
                results[file_path] = opportunities
    
    return results

def save_opportunities(opportunities: Dict[str, List[PatternOpportunity]], output_file: str) -> None:
    """Save pattern opportunities to a JSON file."""
    # Convert opportunities to serializable format
    serializable_results = {}
    for file_path, file_opportunities in opportunities.items():
        serializable_results[file_path] = [opp.to_dict() for opp in file_opportunities]
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(serializable_results, f, indent=2)
    
    logger.info(f"Saved pattern opportunities to {output_file}")

def generate_html_report(opportunities: Dict[str, List[PatternOpportunity]], output_file: str) -> None:
    """Generate an HTML report from the opportunities."""
    # Create HTML header
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pattern Recommendation Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        
        h1, h2, h3 {
            color: #2c3e50;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .file-section {
            margin-bottom: 30px;
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .file-header {
            background-color: #f8f9fa;
            padding: 10px 15px;
            border-bottom: 1px solid #ddd;
            font-weight: bold;
        }
        
        .opportunity {
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        
        .opportunity:last-child {
            border-bottom: none;
        }
        
        .pattern-name {
            font-weight: bold;
            color: #3498db;
            margin-bottom: 5px;
        }
        
        .confidence {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-left: 10px;
        }
        
        .high-confidence {
            background-color: #d4edda;
            color: #155724;
        }
        
        .medium-confidence {
            background-color: #fff3cd;
            color: #856404;
        }
        
        .low-confidence {
            background-color: #f8d7da;
            color: #721c24;
        }
        
        .location {
            color: #6c757d;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .description {
            margin-bottom: 10px;
        }
        
        .benefits {
            margin-bottom: 15px;
        }
        
        .benefits-list {
            margin: 0;
            padding-left: 20px;
        }
        
        .code-snippet {
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 15px;
            overflow-x: auto;
            font-family: monospace;
            white-space: pre;
            font-size: 14px;
        }
        
        .implementation-tabs {
            display: flex;
            border-bottom: 1px solid #ddd;
            margin-bottom: 10px;
        }
        
        .tab {
            padding: 8px 12px;
            cursor: pointer;
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-bottom: none;
            border-radius: 4px 4px 0 0;
            margin-right: 5px;
        }
        
        .tab.active {
            background-color: white;
            border-bottom-color: white;
        }
        
        .implementation {
            display: none;
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            overflow-x: auto;
            font-family: monospace;
            white-space: pre;
            font-size: 14px;
        }
        
        .implementation.active {
            display: block;
        }
        
        .summary {
            background-color: #e3f2fd;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }
        
        .summary h2 {
            margin-top: 0;
        }
        
        .pattern-count {
            margin-right: 15px;
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Pattern Recommendation Report</h1>
"""

    # Add summary section
    total_opportunities = sum(len(opps) for opps in opportunities.values())
    pattern_counts = {}
    for file_opps in opportunities.values():
        for opp in file_opps:
            pattern_counts[opp.pattern_name] = pattern_counts.get(opp.pattern_name, 0) + 1
    
    html_content += f"""
        <div class="summary">
            <h2>Summary</h2>
            <p>
                Analyzed {len(opportunities)} files and found {total_opportunities} pattern opportunities.
            </p>
            <p>
"""
    
    for pattern, count in pattern_counts.items():
        html_content += f'                <span class="pattern-count"><strong>{pattern}:</strong> {count}</span>\n'
    
    html_content += """
            </p>
        </div>
"""
    
    # Add file sections
    for file_path, file_opportunities in opportunities.items():
        rel_path = os.path.relpath(file_path)
        html_content += f"""
        <div class="file-section">
            <div class="file-header">{rel_path}</div>
"""
        
        for opportunity in file_opportunities:
            # Determine confidence class
            confidence_class = "high-confidence"
            if opportunity.confidence < 0.7:
                confidence_class = "low-confidence"
            elif opportunity.confidence < 0.8:
                confidence_class = "medium-confidence"
            
            html_content += f"""
            <div class="opportunity">
                <div class="pattern-name">
                    {opportunity.pattern_name} Pattern
                    <span class="confidence {confidence_class}">
                        Confidence: {opportunity.confidence:.2f}
                    </span>
                </div>
                <div class="location">
                    Lines {opportunity.line_range[0]}-{opportunity.line_range[1]}
                </div>
                <div class="description">
                    {opportunity.description}
                </div>
                <div class="benefits">
                    <strong>Benefits:</strong>
                    <ul class="benefits-list">
"""
            
            for benefit in opportunity.benefits:
                html_content += f'                        <li>{benefit}</li>\n'
            
            html_content += """
                    </ul>
                </div>
                <h4>Current Code:</h4>
                <div class="code-snippet">{}</div>
                <h4>Recommended Implementation:</h4>
                <div class="implementation active">{}</div>
            </div>
""".format(opportunity.code_snippet.replace("<", "&lt;").replace(">", "&gt;"), 
           opportunity.recommended_implementation.replace("<", "&lt;").replace(">", "&gt;"))
        
        html_content += """
        </div>
"""
    
    # Add footer and JavaScript
    html_content += """
    </div>
    
    <script>
        // Tab functionality
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                // Get the tab container
                const tabContainer = tab.closest('.implementation-tabs');
                
                // Remove active class from all tabs
                tabContainer.querySelectorAll('.tab').forEach(t => {
                    t.classList.remove('active');
                });
                
                // Add active class to clicked tab
                tab.classList.add('active');
                
                // Get the implementation container
                const implementationContainer = tabContainer.nextElementSibling;
                
                // Get the implementation divs
                const implementations = implementationContainer.querySelectorAll('.implementation');
                
                // Remove active class from all implementations
                implementations.forEach(impl => {
                    impl.classList.remove('active');
                });
                
                // Add active class to the matching implementation
                const index = Array.from(tabContainer.querySelectorAll('.tab')).indexOf(tab);
                implementations[index].classList.add('active');
            });
        });
    </script>
</body>
</html>
"""
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"Generated HTML report at {output_file}")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pattern Recommendation System")
    parser.add_argument("target", help="File or directory to analyze")
    parser.add_argument("--format", choices=["json", "html"], default="html",
                      help="Output format (default: html)")
    parser.add_argument("--output", "-o", default="pattern_opportunities.html",
                      help="Output file path (default: pattern_opportunities.html or pattern_opportunities.json)")
    
    args = parser.parse_args()
    
    # Set default output file based on format
    if args.output == "pattern_opportunities.html" and args.format == "json":
        args.output = "pattern_opportunities.json"
    
    # Check if target exists
    if not os.path.exists(args.target):
        logger.error(f"Target does not exist: {args.target}")
        return 1
    
    # Analyze target
    if os.path.isfile(args.target):
        opportunities = {args.target: detect_opportunities(args.target)}
    else:
        opportunities = analyze_directory_for_opportunities(args.target)
    
    # Check if any opportunities were found
    if not any(opportunities.values()):
        logger.info("No pattern opportunities found")
        return 0
    
    # Save results
    if args.format == "json":
        save_opportunities(opportunities, args.output)
    else:
        generate_html_report(opportunities, args.output)
    
    # Print summary
    total_opportunities = sum(len(opps) for opps in opportunities.values())
    pattern_counts = {}
    for file_opps in opportunities.values():
        for opp in file_opps:
            pattern_counts[opp.pattern_name] = pattern_counts.get(opp.pattern_name, 0) + 1
    
    logger.info(f"Found {total_opportunities} pattern opportunities in {len(opportunities)} files")
    for pattern, count in pattern_counts.items():
        logger.info(f"  {pattern}: {count}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())