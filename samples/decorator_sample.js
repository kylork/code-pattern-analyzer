/**
 * Sample implementations of the Decorator pattern in JavaScript.
 * 
 * The Decorator pattern allows behavior to be added to individual objects,
 * either statically or dynamically, without affecting the behavior of other
 * objects from the same class.
 */

// Implementation 1: Classic Decorator Pattern with Component interface

/**
 * Component interface (abstract class in JavaScript)
 */
class Component {
  operation() {
    throw new Error('Component.operation must be implemented');
  }
}

/**
 * Concrete implementation of the Component interface
 */
class ConcreteComponent extends Component {
  operation() {
    return "ConcreteComponent";
  }
}

/**
 * Base Decorator class that follows the same interface as Component
 */
class Decorator extends Component {
  constructor(component) {
    super();
    this._component = component;
  }
  
  // Default behavior is to delegate to the wrapped component
  operation() {
    return this._component.operation();
  }
}

/**
 * Concrete decorator that adds behavior before/after the component
 */
class ConcreteDecoratorA extends Decorator {
  operation() {
    return `ConcreteDecoratorA(${this._component.operation()})`;
  }
}

/**
 * Another concrete decorator with additional state and behavior
 */
class ConcreteDecoratorB extends Decorator {
  constructor(component) {
    super(component);
    this._additionalState = "Some state";
  }
  
  operation() {
    return `ConcreteDecoratorB(${this._component.operation()})`;
  }
  
  additionalBehavior() {
    return `Additional behavior: ${this._additionalState}`;
  }
}

// Implementation 2: Function Decorators (Higher-order functions)

/**
 * Function decorator that adds logging to a function
 */
function loggingDecorator(func) {
  return function(...args) {
    console.log(`Calling ${func.name} with ${JSON.stringify(args)}`);
    const result = func.apply(this, args);
    console.log(`${func.name} returned ${result}`);
    return result;
  };
}

/**
 * Example function that will be decorated with logging
 */
function exampleFunction(x, y) {
  return x + y;
}

// Apply the decorator
const decoratedFunction = loggingDecorator(exampleFunction);

// Implementation 3: Method Decorators with Object.defineProperty

/**
 * Method decorator that adds timing to a method
 */
function timeDecorator(target, name, descriptor) {
  const original = descriptor.value;
  
  descriptor.value = function(...args) {
    const start = performance.now();
    const result = original.apply(this, args);
    const end = performance.now();
    console.log(`${name} took ${end - start} ms`);
    return result;
  };
  
  return descriptor;
}

/**
 * Example class with a decorated method (using ES7 decorators)
 * Note: This syntax requires Babel/TypeScript with decorator support
 */
class Timer {
  // This is a comment showing how the decorator would be used in ES7
  // @timeDecorator
  slowMethod(iterations) {
    let result = 0;
    for (let i = 0; i < iterations; i++) {
      result += i;
    }
    return result;
  }
}

// Manual application of the decorator (since JS doesn't support @ syntax natively)
// This is equivalent to the @timeDecorator annotation
Object.defineProperty(
  Timer.prototype, 
  'slowMethod', 
  timeDecorator(Timer.prototype, 'slowMethod', 
    Object.getOwnPropertyDescriptor(Timer.prototype, 'slowMethod')
  )
);

// Implementation 4: Object composition with explicit decoration

/**
 * Text processor that can be decorated
 */
class TextProcessor {
  process(text) {
    return text;
  }
}

/**
 * Decorator that adds uppercase functionality
 */
class UppercaseDecorator {
  constructor(processor) {
    this.processor = processor;
  }
  
  process(text) {
    return this.processor.process(text).toUpperCase();
  }
}

/**
 * Decorator that adds HTML markup
 */
class BoldDecorator {
  constructor(processor) {
    this.processor = processor;
  }
  
  process(text) {
    return `<b>${this.processor.process(text)}</b>`;
  }
}

// Usage Example
function runExamples() {
  // Example 1: Classic Decorator Pattern
  console.log("Example 1: Classic Decorator Pattern");
  const simple = new ConcreteComponent();
  const decorated1 = new ConcreteDecoratorA(simple);
  const decorated2 = new ConcreteDecoratorB(decorated1);
  
  console.log(`Simple component: ${simple.operation()}`);
  console.log(`Decorated once: ${decorated1.operation()}`);
  console.log(`Decorated twice: ${decorated2.operation()}`);
  console.log(`Additional behavior: ${decorated2.additionalBehavior()}`);
  
  console.log("-".repeat(50));
  
  // Example 2: Function Decorators
  console.log("Example 2: Function Decorators");
  const result = decoratedFunction(5, 3);
  console.log(`Result: ${result}`);
  
  console.log("-".repeat(50));
  
  // Example 3: Method Decorators
  console.log("Example 3: Method Decorators");
  const timer = new Timer();
  timer.slowMethod(1000000);
  
  console.log("-".repeat(50));
  
  // Example 4: Object Composition
  console.log("Example 4: Object Composition");
  const processor = new TextProcessor();
  const uppercaseProcessor = new UppercaseDecorator(processor);
  const boldUppercaseProcessor = new BoldDecorator(uppercaseProcessor);
  
  const text = "Hello, Decorator Pattern!";
  console.log(`Original: ${processor.process(text)}`);
  console.log(`Uppercase: ${uppercaseProcessor.process(text)}`);
  console.log(`Bold Uppercase: ${boldUppercaseProcessor.process(text)}`);
}

// Uncomment to run the examples
// runExamples();