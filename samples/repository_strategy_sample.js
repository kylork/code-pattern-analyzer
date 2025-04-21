/**
 * Sample implementation of the Repository-based Strategy pattern in JavaScript.
 * 
 * The Repository-based Strategy pattern extends the traditional Strategy pattern
 * by centralizing the creation and management of strategy objects in a repository.
 * This provides a way to decouple strategy selection from strategy implementation
 * and enables runtime registration of new strategies.
 */

/**
 * Strategy interface for sorting algorithms
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
 * Repository of sorting strategies.
 */
class SortStrategyRepository {
  // Private class field for storing strategies
  static #strategies = {};
  
  /**
   * Register a strategy with the repository.
   * @param {string} key - Identifier for the strategy
   * @param {typeof SortStrategy} strategyClass - Strategy class to register
   */
  static register(key, strategyClass) {
    SortStrategyRepository.#strategies[key] = strategyClass;
  }
  
  /**
   * Get a strategy instance by key.
   * @param {string} key - Identifier for the strategy
   * @returns {SortStrategy} Instance of the requested strategy
   * @throws {Error} If the strategy key is not found
   */
  static get(key) {
    if (!SortStrategyRepository.#strategies[key]) {
      throw new Error(`Strategy '${key}' not found in repository`);
    }
    
    return new SortStrategyRepository.#strategies[key]();
  }
  
  /**
   * Get a list of available strategy keys.
   * @returns {string[]} Array of available strategy keys
   */
  static availableStrategies() {
    return Object.keys(SortStrategyRepository.#strategies);
  }
}

/**
 * Context that uses a strategy from the repository.
 */
class Sorter {
  /**
   * Initialize with a strategy type from the repository.
   * @param {string} strategyType - Key for the strategy in the repository
   */
  constructor(strategyType) {
    this._strategyType = strategyType;
    this._strategy = SortStrategyRepository.get(strategyType);
  }
  
  /**
   * Get the current strategy type.
   * @returns {string} Current strategy type key
   */
  get strategyType() {
    return this._strategyType;
  }
  
  /**
   * Change the strategy by selecting a new one from the repository.
   * @param {string} strategyType - Key for the new strategy in the repository
   */
  set strategyType(strategyType) {
    this._strategyType = strategyType;
    this._strategy = SortStrategyRepository.get(strategyType);
  }
  
  /**
   * Sort the data using the current strategy.
   * @param {number[]} data - Array of numbers to sort
   * @returns {number[]} Sorted array
   */
  sort(data) {
    return this._strategy.sort(data);
  }
}

// Register strategies with the repository
SortStrategyRepository.register("bubble", BubbleSortStrategy);
SortStrategyRepository.register("quick", QuickSortStrategy);
SortStrategyRepository.register("merge", MergeSortStrategy);

// Dynamic strategy registration example
class HeapSortStrategy extends SortStrategy {
  /**
   * Heapify subtree rooted at index i.
   * @param {number[]} arr - Array to heapify
   * @param {number} n - Size of heap
   * @param {number} i - Root index
   */
  _heapify(arr, n, i) {
    let largest = i;
    const left = 2 * i + 1;
    const right = 2 * i + 2;
    
    if (left < n && arr[largest] < arr[left]) {
      largest = left;
    }
    
    if (right < n && arr[largest] < arr[right]) {
      largest = right;
    }
    
    if (largest !== i) {
      [arr[i], arr[largest]] = [arr[largest], arr[i]];
      this._heapify(arr, n, largest);
    }
  }
  
  /**
   * Sort using heap sort algorithm.
   * @param {number[]} data - Array to sort
   * @returns {number[]} Sorted array
   */
  sort(data) {
    const result = [...data];
    const n = result.length;
    
    // Build max heap
    for (let i = Math.floor(n / 2) - 1; i >= 0; i--) {
      this._heapify(result, n, i);
    }
    
    // Extract elements one by one
    for (let i = n - 1; i > 0; i--) {
      [result[0], result[i]] = [result[i], result[0]];
      this._heapify(result, i, 0);
    }
    
    return result;
  }
}

// Register the new strategy at runtime
SortStrategyRepository.register("heap", HeapSortStrategy);

/**
 * Example of a generic data processor using the repository pattern
 */

// Strategy interface for data processing
class ProcessingStrategy {
  process(data) {
    throw new Error('process() method must be implemented');
  }
}

// Repository of data processing strategies
class ProcessingStrategyRepository {
  static #strategies = {};
  
  static register(key, strategyClass) {
    ProcessingStrategyRepository.#strategies[key] = strategyClass;
  }
  
  static get(key) {
    if (!ProcessingStrategyRepository.#strategies[key]) {
      throw new Error(`Strategy '${key}' not found in repository`);
    }
    
    return new ProcessingStrategyRepository.#strategies[key]();
  }
}

// Context that uses a processing strategy from the repository
class DataProcessor {
  constructor(strategyType) {
    this._strategyType = strategyType;
    this._strategy = ProcessingStrategyRepository.get(strategyType);
  }
  
  process(data) {
    return this._strategy.process(data);
  }
}

// Usage example
function runExamples() {
  // Example data
  const data = [7, 1, 5, 2, 4, 3, 6];
  
  // Create sorter with bubble sort strategy
  const sorter = new Sorter("bubble");
  console.log("Original data:", data);
  console.log("Bubble sort:", sorter.sort(data));
  
  // Change strategy to quick sort
  sorter.strategyType = "quick";
  console.log("Quick sort:", sorter.sort(data));
  
  // Change strategy to merge sort
  sorter.strategyType = "merge";
  console.log("Merge sort:", sorter.sort(data));
  
  // Change strategy to heap sort (dynamically registered)
  sorter.strategyType = "heap";
  console.log("Heap sort:", sorter.sort(data));
  
  // List all available strategies
  console.log("Available strategies:", SortStrategyRepository.availableStrategies());
}

// Uncomment to run the examples
// runExamples();