/**
 * Sample implementations of the Strategy pattern in JavaScript.
 * 
 * The Strategy pattern defines a family of algorithms, encapsulates each one,
 * and makes them interchangeable. It lets the algorithm vary independently
 * from clients that use it.
 */

// Implementation 1: Class-based Strategy Pattern

/**
 * Strategy interface (abstract class in JavaScript)
 */
class SortStrategy {
  sort(data) {
    throw new Error('sort() method must be implemented');
  }
}

/**
 * Concrete strategy implementing bubble sort
 */
class BubbleSortStrategy extends SortStrategy {
  sort(data) {
    // Create a copy to avoid modifying the original array
    const result = [...data];
    const n = result.length;
    
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n - i - 1; j++) {
        if (result[j] > result[j + 1]) {
          // Swap elements
          [result[j], result[j + 1]] = [result[j + 1], result[j]];
        }
      }
    }
    
    return result;
  }
}

/**
 * Concrete strategy implementing quick sort
 */
class QuickSortStrategy extends SortStrategy {
  sort(data) {
    // Create a copy to avoid modifying the original array
    const result = [...data];
    
    if (result.length <= 1) {
      return result;
    }
    
    const pivot = result[Math.floor(result.length / 2)];
    const left = result.filter(x => x < pivot);
    const middle = result.filter(x => x === pivot);
    const right = result.filter(x => x > pivot);
    
    return [...this.sort(left), ...middle, ...this.sort(right)];
  }
}

/**
 * Concrete strategy implementing merge sort
 */
class MergeSortStrategy extends SortStrategy {
  sort(data) {
    // Create a copy to avoid modifying the original array
    const result = [...data];
    
    if (result.length <= 1) {
      return result;
    }
    
    // Split the array in half
    const mid = Math.floor(result.length / 2);
    const left = this.sort(result.slice(0, mid));
    const right = this.sort(result.slice(mid));
    
    // Merge the sorted halves
    return this._merge(left, right);
  }
  
  _merge(left, right) {
    const merged = [];
    let i = 0, j = 0;
    
    // Compare elements from both arrays and add the smaller one to the result
    while (i < left.length && j < right.length) {
      if (left[i] <= right[j]) {
        merged.push(left[i]);
        i++;
      } else {
        merged.push(right[j]);
        j++;
      }
    }
    
    // Add any remaining elements
    return [...merged, ...left.slice(i), ...right.slice(j)];
  }
}

/**
 * Context that uses a sort strategy
 */
class SortContext {
  constructor(strategy = null) {
    this._strategy = strategy || new BubbleSortStrategy();
  }
  
  get strategy() {
    return this._strategy;
  }
  
  set strategy(strategy) {
    this._strategy = strategy;
  }
  
  sort(data) {
    return this._strategy.sort(data);
  }
}

// Implementation 2: Function-based Strategy Pattern

/**
 * Bubble sort implementation
 */
function bubbleSort(data) {
  const result = [...data];
  const n = result.length;
  
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n - i - 1; j++) {
      if (result[j] > result[j + 1]) {
        [result[j], result[j + 1]] = [result[j + 1], result[j]];
      }
    }
  }
  
  return result;
}

/**
 * Quick sort implementation
 */
function quickSort(data) {
  const result = [...data];
  
  if (result.length <= 1) {
    return result;
  }
  
  const pivot = result[Math.floor(result.length / 2)];
  const left = result.filter(x => x < pivot);
  const middle = result.filter(x => x === pivot);
  const right = result.filter(x => x > pivot);
  
  return [...quickSort(left), ...middle, ...quickSort(right)];
}

/**
 * Merge sort implementation
 */
function mergeSort(data) {
  const result = [...data];
  
  if (result.length <= 1) {
    return result;
  }
  
  const mid = Math.floor(result.length / 2);
  const left = mergeSort(result.slice(0, mid));
  const right = mergeSort(result.slice(mid));
  
  return merge(left, right);
}

/**
 * Helper function to merge two sorted arrays
 */
function merge(left, right) {
  const merged = [];
  let i = 0, j = 0;
  
  while (i < left.length && j < right.length) {
    if (left[i] <= right[j]) {
      merged.push(left[i]);
      i++;
    } else {
      merged.push(right[j]);
      j++;
    }
  }
  
  return [...merged, ...left.slice(i), ...right.slice(j)];
}

/**
 * Context that uses a sorting function as a strategy
 */
class FunctionalSortContext {
  constructor(strategy = bubbleSort) {
    this._strategy = strategy;
  }
  
  get strategy() {
    return this._strategy;
  }
  
  set strategy(strategy) {
    this._strategy = strategy;
  }
  
  sort(data) {
    return this._strategy(data);
  }
}

// Implementation 3: Object-based Strategy Pattern

/**
 * Payment processor using strategies defined as object methods
 */
class PaymentProcessor {
  constructor(strategy = 'creditCard') {
    // Validate strategy exists
    if (!this.strategies[strategy]) {
      throw new Error(`Unknown payment strategy: ${strategy}`);
    }
    this._strategy = strategy;
  }
  
  // Available payment strategies
  get strategies() {
    return {
      creditCard: (amount) => `Processing credit card payment of $${amount}`,
      paypal: (amount) => `Processing PayPal payment of $${amount}`,
      bankTransfer: (amount) => `Processing bank transfer of $${amount}`,
      cryptocurrency: (amount) => `Processing cryptocurrency payment of $${amount}`
    };
  }
  
  get strategy() {
    return this._strategy;
  }
  
  set strategy(strategy) {
    if (!this.strategies[strategy]) {
      throw new Error(`Unknown payment strategy: ${strategy}`);
    }
    this._strategy = strategy;
  }
  
  processPayment(amount) {
    return this.strategies[this._strategy](amount);
  }
}

// Implementation 4: Strategy with Dependency Injection

/**
 * Formatter strategies for different output formats
 */
class TextFormatter {
  format(text) {
    return text;
  }
}

class HTMLFormatter {
  format(text) {
    return `<p>${text}</p>`;
  }
}

class MarkdownFormatter {
  format(text) {
    return `*${text}*`;
  }
}

/**
 * Report generator that uses a formatter strategy
 */
class ReportGenerator {
  constructor(formatter) {
    this.formatter = formatter;
  }
  
  generateReport(data) {
    return this.formatter.format(data);
  }
}

// Usage examples
function runExamples() {
  // Example 1: Class-based Strategy Pattern
  console.log("Example 1: Class-based Strategy Pattern");
  const data = [7, 1, 5, 2, 4, 3, 6];
  
  const context = new SortContext();
  console.log("Original data:", data);
  console.log("Bubble sort:", context.sort(data));
  
  context.strategy = new QuickSortStrategy();
  console.log("Quick sort:", context.sort(data));
  
  context.strategy = new MergeSortStrategy();
  console.log("Merge sort:", context.sort(data));
  
  console.log("-".repeat(50));
  
  // Example 2: Function-based Strategy Pattern
  console.log("Example 2: Function-based Strategy Pattern");
  
  const funcContext = new FunctionalSortContext();
  console.log("Original data:", data);
  console.log("Bubble sort:", funcContext.sort(data));
  
  funcContext.strategy = quickSort;
  console.log("Quick sort:", funcContext.sort(data));
  
  funcContext.strategy = mergeSort;
  console.log("Merge sort:", funcContext.sort(data));
  
  console.log("-".repeat(50));
  
  // Example 3: Object-based Strategy Pattern
  console.log("Example 3: Object-based Strategy Pattern");
  
  const payment = new PaymentProcessor();
  console.log(payment.processPayment(100));
  
  payment.strategy = 'paypal';
  console.log(payment.processPayment(100));
  
  payment.strategy = 'bankTransfer';
  console.log(payment.processPayment(100));
  
  payment.strategy = 'cryptocurrency';
  console.log(payment.processPayment(100));
  
  console.log("-".repeat(50));
  
  // Example 4: Strategy with Dependency Injection
  console.log("Example 4: Strategy with Dependency Injection");
  
  const textReport = new ReportGenerator(new TextFormatter());
  console.log(textReport.generateReport("Sample Report"));
  
  const htmlReport = new ReportGenerator(new HTMLFormatter());
  console.log(htmlReport.generateReport("Sample Report"));
  
  const markdownReport = new ReportGenerator(new MarkdownFormatter());
  console.log(markdownReport.generateReport("Sample Report"));
}

// Uncomment to run the examples
// runExamples();