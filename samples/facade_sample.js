/**
 * Sample implementations of the Facade pattern in JavaScript.
 * 
 * The Facade pattern provides a simplified interface to a complex subsystem.
 * It doesn't encapsulate the subsystem but provides a unified interface to make
 * the subsystem easier to use.
 */

// Implementation 1: Classic Facade Pattern

/**
 * A complex subsystem component
 */
class ComplexSubsystemA {
  operation1() {
    return "Subsystem A: Operation 1";
  }
  
  operation2() {
    return "Subsystem A: Operation 2";
  }
}

/**
 * Another complex subsystem component
 */
class ComplexSubsystemB {
  operation1() {
    return "Subsystem B: Operation 1";
  }
  
  operation2() {
    return "Subsystem B: Operation 2";
  }
}

/**
 * Yet another complex subsystem component
 */
class ComplexSubsystemC {
  operation1() {
    return "Subsystem C: Operation 1";
  }
}

/**
 * The Facade class provides a simple interface to the complex subsystem
 */
class Facade {
  constructor() {
    this.subsystemA = new ComplexSubsystemA();
    this.subsystemB = new ComplexSubsystemB();
    this.subsystemC = new ComplexSubsystemC();
  }
  
  /**
   * The facade methods that provide a simplified interface.
   * They delegate to subsystem objects to perform complex operations.
   */
  operation() {
    const results = [];
    results.push("Facade initializes subsystems:");
    results.push(this.subsystemA.operation1());
    results.push(this.subsystemB.operation1());
    results.push("Facade orders subsystems to perform the action:");
    results.push(this.subsystemA.operation2());
    results.push(this.subsystemB.operation2());
    results.push(this.subsystemC.operation1());
    return results.join('\n');
  }
}

// Implementation 2: Module Facade Pattern with ES6 Modules

/**
 * API service for external HTTP requests
 */
class APIService {
  constructor(baseURL) {
    this.baseURL = baseURL;
  }
  
  get(endpoint) {
    return `GET ${this.baseURL}/${endpoint}`;
  }
  
  post(endpoint, data) {
    return `POST ${this.baseURL}/${endpoint} with ${JSON.stringify(data)}`;
  }
  
  put(endpoint, data) {
    return `PUT ${this.baseURL}/${endpoint} with ${JSON.stringify(data)}`;
  }
  
  delete(endpoint) {
    return `DELETE ${this.baseURL}/${endpoint}`;
  }
}

/**
 * Authentication service
 */
class AuthService {
  constructor() {
    this.token = null;
  }
  
  login(credentials) {
    this.token = "sample-jwt-token";
    return `Logged in as ${credentials.username}`;
  }
  
  logout() {
    this.token = null;
    return "Logged out";
  }
  
  getToken() {
    return this.token;
  }
}

/**
 * Storage service for local data persistence
 */
class StorageService {
  setItem(key, value) {
    return `Stored ${key}=${value}`;
  }
  
  getItem(key) {
    return `Retrieved ${key}`;
  }
  
  removeItem(key) {
    return `Removed ${key}`;
  }
  
  clear() {
    return "Storage cleared";
  }
}

/**
 * User service facade that simplifies working with users through multiple services
 */
class UserServiceFacade {
  constructor(apiBaseURL) {
    this.api = new APIService(apiBaseURL);
    this.auth = new AuthService();
    this.storage = new StorageService();
  }
  
  /**
   * Login a user and store their information
   */
  login(username, password) {
    // Authenticate
    const result = this.auth.login({ username, password });
    
    // Store token
    this.storage.setItem('auth_token', this.auth.getToken());
    
    // Load user data
    const userData = this.api.get(`users/${username}`);
    
    // Store user data
    this.storage.setItem('user_data', userData);
    
    return `User ${username} logged in successfully`;
  }
  
  /**
   * Register a new user
   */
  register(userData) {
    // Create user account
    const result = this.api.post('users', userData);
    
    // Store registration status
    this.storage.setItem('registration_status', 'complete');
    
    return `User ${userData.username} registered successfully`;
  }
  
  /**
   * Logout the current user
   */
  logout() {
    // Logout from auth service
    this.auth.logout();
    
    // Clear stored data
    this.storage.removeItem('auth_token');
    this.storage.removeItem('user_data');
    
    return "User logged out successfully";
  }
}

// Implementation 3: Object Literal Facade Pattern

/**
 * These would normally be more complex and possibly in separate files
 */
// Audio handling
const audioEngine = {
  init() {
    return "Audio engine initialized";
  },
  playSound(soundId) {
    return `Playing sound: ${soundId}`;
  },
  stopSound(soundId) {
    return `Stopping sound: ${soundId}`;
  },
  setVolume(level) {
    return `Setting volume to ${level}`;
  }
};

// Graphics handling
const graphicsEngine = {
  init(width, height) {
    return `Graphics initialized with resolution ${width}x${height}`;
  },
  drawSprite(spriteId, x, y) {
    return `Drawing sprite ${spriteId} at position (${x}, ${y})`;
  },
  clearScreen() {
    return "Screen cleared";
  }
};

// Input handling
const inputHandler = {
  init() {
    return "Input handler initialized";
  },
  bindKey(key, action) {
    return `Key ${key} bound to action: ${action}`;
  },
  unbindKey(key) {
    return `Key ${key} unbound`;
  }
};

/**
 * Game facade using object literal that simplifies working with complex subsystems
 */
const gameFacade = {
  // Initialize all subsystems
  init(width, height) {
    const results = [];
    results.push(audioEngine.init());
    results.push(graphicsEngine.init(width, height));
    results.push(inputHandler.init());
    
    // Bind default keys
    results.push(inputHandler.bindKey("SPACE", "JUMP"));
    results.push(inputHandler.bindKey("W", "MOVE_UP"));
    results.push(inputHandler.bindKey("A", "MOVE_LEFT"));
    
    return results.join('\n');
  },
  
  // Start a new game level
  startLevel(levelId) {
    const results = [];
    results.push(graphicsEngine.clearScreen());
    results.push(`Loading level ${levelId}`);
    results.push(audioEngine.playSound("LEVEL_START"));
    return results.join('\n');
  },
  
  // Handle player jumping
  jump() {
    const results = [];
    results.push(audioEngine.playSound("JUMP"));
    results.push(graphicsEngine.drawSprite("PLAYER_JUMP", 100, 150));
    return results.join('\n');
  }
};

// Usage examples
function runExamples() {
  // Example 1: Classic Facade
  console.log("Example 1: Classic Facade");
  const facade = new Facade();
  console.log(facade.operation());
  
  console.log("-".repeat(50));
  
  // Example 2: Module Facade
  console.log("Example 2: Module Facade");
  const userService = new UserServiceFacade("https://api.example.com");
  console.log(userService.register({ username: "john_doe", email: "john@example.com" }));
  console.log(userService.login("john_doe", "password123"));
  console.log(userService.logout());
  
  console.log("-".repeat(50));
  
  // Example 3: Object Literal Facade
  console.log("Example 3: Object Literal Facade");
  console.log(gameFacade.init(1920, 1080));
  console.log(gameFacade.startLevel(1));
  console.log(gameFacade.jump());
}

// Uncomment to run the examples
// runExamples();