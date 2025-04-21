/**
 * Sample implementations of the Adapter pattern in JavaScript.
 * 
 * The Adapter pattern converts the interface of a class into another interface
 * that clients expect. It allows classes to work together that couldn't otherwise
 * because of incompatible interfaces.
 */

// Implementation 1: Class Adapter Pattern

/**
 * Target interface that the client uses
 */
class Target {
  request() {
    throw new Error('Target.request() must be implemented');
  }
}

/**
 * Existing class with an incompatible interface
 */
class Adaptee {
  specificRequest() {
    return "Adaptee's specific behavior";
  }
}

/**
 * Adapter that implements the Target interface and adapts the Adaptee
 */
class Adapter extends Target {
  constructor() {
    super();
    this.adaptee = new Adaptee();
  }
  
  request() {
    return `Adapter: (TRANSLATED) ${this.adaptee.specificRequest()}`;
  }
}

// Implementation 2: Object Adapter Pattern (using composition)

/**
 * Target interface for object adapter
 */
class ObjectTarget {
  request() {
    throw new Error('ObjectTarget.request() must be implemented');
  }
}

/**
 * Legacy service with incompatible interface
 */
class LegacyService {
  legacyOperation() {
    return "Legacy service operation";
  }
}

/**
 * Adapter using composition
 */
class ObjectAdapter extends ObjectTarget {
  constructor(adaptee) {
    super();
    this.adaptee = adaptee;
  }
  
  request() {
    return `ObjectAdapter: ${this.adaptee.legacyOperation()}`;
  }
}

// Implementation 3: Function Adapter Pattern

/**
 * Legacy function with incompatible return format
 */
function legacyFunction(value) {
  return { result: value * 2, source: "legacy" };
}

/**
 * Adapter function that calls legacyFunction but returns a compatible format
 */
function adaptedFunction(value) {
  const result = legacyFunction(value);
  return result.result;
}

// Implementation 4: Interface Adapter using modern JavaScript features

/**
 * Modern library API
 */
class ModernLibrary {
  constructor() {
    this.data = [];
  }
  
  async fetchData() {
    // Simulating async data fetch
    return Promise.resolve([
      { id: 1, name: "Item 1" },
      { id: 2, name: "Item 2" },
      { id: 3, name: "Item 3" }
    ]);
  }
  
  process(items) {
    return items.map(item => ({
      ...item,
      processed: true
    }));
  }
}

/**
 * Legacy code expects synchronous operations and different data format
 */
class LegacyCode {
  constructor() {
    this.items = [];
  }
  
  setItems(items) {
    this.items = items;
    console.log(`Got ${items.length} items`);
  }
  
  displayItems() {
    return this.items
      .map(item => `${item.id}: ${item.title}`)
      .join(', ');
  }
}

/**
 * Adapter to make ModernLibrary work with LegacyCode
 */
class ModernAdapter {
  constructor(modernLibrary, legacyCode) {
    this.modernLibrary = modernLibrary;
    this.legacyCode = legacyCode;
  }
  
  // Adapts async operation to sync expectation
  async loadData() {
    const data = await this.modernLibrary.fetchData();
    const processed = this.modernLibrary.process(data);
    
    // Transform data to match legacy format
    const adaptedData = processed.map(item => ({
      id: item.id,
      title: item.name // rename property to match legacy expectation
    }));
    
    this.legacyCode.setItems(adaptedData);
    return adaptedData;
  }
  
  // Forwards to legacy code but could add adaptations
  display() {
    return this.legacyCode.displayItems();
  }
}

// Implementation 5: Object Composition Adapter using object literals

/**
 * Third-party API response format
 */
const thirdPartyApi = {
  getUsers() {
    return [
      { user_id: 1, user_name: "Alice", user_email: "alice@example.com" },
      { user_id: 2, user_name: "Bob", user_email: "bob@example.com" }
    ];
  }
};

/**
 * Adapter for third-party API that transforms to our application format
 */
const userApiAdapter = {
  getUsers() {
    // Get data from third-party API
    const users = thirdPartyApi.getUsers();
    
    // Transform to application format
    return users.map(user => ({
      id: user.user_id,
      name: user.user_name,
      email: user.user_email
    }));
  }
};

// Usage examples
function runExamples() {
  // Example 1: Class Adapter
  console.log("Example 1: Class Adapter");
  const adapter = new Adapter();
  console.log(adapter.request());
  
  console.log("-".repeat(50));
  
  // Example 2: Object Adapter
  console.log("Example 2: Object Adapter");
  const legacyService = new LegacyService();
  const objectAdapter = new ObjectAdapter(legacyService);
  console.log(objectAdapter.request());
  
  console.log("-".repeat(50));
  
  // Example 3: Function Adapter
  console.log("Example 3: Function Adapter");
  console.log(`Direct legacy result: ${JSON.stringify(legacyFunction(5))}`);
  console.log(`Adapted result: ${adaptedFunction(5)}`);
  
  console.log("-".repeat(50));
  
  // Example 4: Modern JavaScript Adapter
  console.log("Example 4: Modern JavaScript Adapter");
  const modernLibrary = new ModernLibrary();
  const legacyCode = new LegacyCode();
  const modernAdapter = new ModernAdapter(modernLibrary, legacyCode);
  
  modernAdapter.loadData().then(() => {
    console.log(modernAdapter.display());
  });
  
  console.log("-".repeat(50));
  
  // Example 5: Object Literal Adapter
  console.log("Example 5: Object Literal Adapter");
  console.log(`Third-party API: ${JSON.stringify(thirdPartyApi.getUsers())}`);
  console.log(`Adapted API: ${JSON.stringify(userApiAdapter.getUsers())}`);
}

// Uncomment to run the examples
// runExamples();