/**
 * Sample JavaScript file with various design patterns.
 */

// Singleton pattern using a class
class Singleton {
  constructor() {
    if (Singleton._instance) {
      return Singleton._instance;
    }
    
    Singleton._instance = this;
    this.value = "Default value";
  }
  
  setValue(value) {
    this.value = value;
  }
  
  getValue() {
    return this.value;
  }
}

// Another Singleton pattern using an IIFE
const SingletonModule = (function() {
  let instance;
  
  function createInstance() {
    return {
      value: "Default value",
      setValue: function(value) {
        this.value = value;
      },
      getValue: function() {
        return this.value;
      }
    };
  }
  
  return {
    getInstance: function() {
      if (!instance) {
        instance = createInstance();
      }
      return instance;
    }
  };
})();

// Factory pattern
class Shape {
  constructor() {
    if (this.constructor === Shape) {
      throw new Error("Cannot instantiate abstract class");
    }
  }
  
  draw() {
    throw new Error("Method 'draw()' must be implemented");
  }
}

class Circle extends Shape {
  constructor(radius) {
    super();
    this.radius = radius;
  }
  
  draw() {
    return `Drawing circle with radius ${this.radius}`;
  }
}

class Rectangle extends Shape {
  constructor(width, height) {
    super();
    this.width = width;
    this.height = height;
  }
  
  draw() {
    return `Drawing rectangle with width ${this.width} and height ${this.height}`;
  }
}

class ShapeFactory {
  static createShape(type, ...args) {
    switch(type) {
      case 'circle':
        return new Circle(...args);
      case 'rectangle':
        return new Rectangle(...args);
      default:
        throw new Error(`Unknown shape type: ${type}`);
    }
  }
}

// Example of deep nesting (code smell)
function processOrder(order) {
  if (order) {
    if (order.items) {
      if (order.items.length > 0) {
        if (order.customer) {
          if (order.customer.id) {
            if (order.customer.address) {
              if (order.payment) {
                if (order.payment.method) {
                  if (order.payment.method === 'credit') {
                    if (order.payment.card) {
                      if (order.payment.card.valid) {
                        // Process the order
                        return true;
                      } else {
                        return false; // Invalid card
                      }
                    } else {
                      return false; // No card info
                    }
                  } else if (order.payment.method === 'cash') {
                    // Process cash order
                    return true;
                  } else {
                    return false; // Unknown payment method
                  }
                } else {
                  return false; // No payment method
                }
              } else {
                return false; // No payment info
              }
            } else {
              return false; // No address
            }
          } else {
            return false; // No customer ID
          }
        } else {
          return false; // No customer info
        }
      } else {
        return false; // Empty order
      }
    } else {
      return false; // No items
    }
  } else {
    return false; // No order
  }
}

// Example of complex condition (code smell)
function checkEligibility(user, products, settings) {
  if ((user.age >= 18 && user.age <= 65 || user.vipStatus && user.age >= 15) &&
      (user.country in settings.allowedCountries && !settings.blockedCountries.includes(user.country)) &&
      (products.length > 0 && products.some(p => settings.eligibleCategories.includes(p.category))) &&
      (!user.isBanned && !user.accountSuspended && user.emailVerified) &&
      (Date.now() - user.registrationTime >= settings.minimumAccountAge || user.referralCount >= settings.minimumReferrals)) {
    return true;
  } else {
    return false;
  }
}

// Export for node.js
module.exports = {
  Singleton,
  SingletonModule,
  ShapeFactory,
  Circle,
  Rectangle,
  processOrder,
  checkEligibility
};