/**
 * Sample implementations of the Observer pattern in JavaScript.
 * 
 * The Observer pattern defines a one-to-many dependency between objects
 * so that when one object changes state, all its dependents are notified
 * and updated automatically.
 */

// Implementation 1: Classic Observer Pattern with Subject and Observer classes

class Subject {
  constructor() {
    this.observers = [];
  }

  attach(observer) {
    const isExist = this.observers.includes(observer);
    if (!isExist) {
      this.observers.push(observer);
    }
  }

  detach(observer) {
    const observerIndex = this.observers.indexOf(observer);
    if (observerIndex !== -1) {
      this.observers.splice(observerIndex, 1);
    }
  }

  notify() {
    for (const observer of this.observers) {
      observer.update(this);
    }
  }
}

class Observer {
  update(subject) {
    throw new Error('Observer must implement update method');
  }
}

// Concrete implementations of the Observer pattern

class WeatherStation extends Subject {
  constructor() {
    super();
    this._temperature = 0;
  }
  
  get temperature() {
    return this._temperature;
  }
  
  set temperature(value) {
    if (this._temperature !== value) {
      this._temperature = value;
      this.notify();
    }
  }
}

class TemperatureDisplay extends Observer {
  update(subject) {
    console.log(`Temperature Display: ${subject.temperature}°C`);
  }
}

class TemperatureLogger extends Observer {
  constructor() {
    super();
    this.log = [];
  }
  
  update(subject) {
    this.log.push(subject.temperature);
    console.log(`Temperature Logger: Recorded ${subject.temperature}°C`);
  }
}

// Implementation 2: Observer pattern using EventEmitter

class EventEmitter {
  constructor() {
    this.events = {};
  }
  
  on(eventName, callback) {
    if (!this.events[eventName]) {
      this.events[eventName] = [];
    }
    this.events[eventName].push(callback);
  }
  
  off(eventName, callback) {
    if (!this.events[eventName]) return;
    
    const index = this.events[eventName].indexOf(callback);
    if (index !== -1) {
      this.events[eventName].splice(index, 1);
    }
  }
  
  emit(eventName, ...args) {
    if (!this.events[eventName]) return;
    
    for (const callback of this.events[eventName]) {
      callback(...args);
    }
  }
}

// Example using EventEmitter

class StockMarket extends EventEmitter {
  constructor() {
    super();
    this._price = 0;
  }
  
  get price() {
    return this._price;
  }
  
  set price(value) {
    if (this._price !== value) {
      const oldPrice = this._price;
      this._price = value;
      this.emit('priceChanged', value, oldPrice);
    }
  }
}

// Implementation 3: Observer pattern using interfaces

// In JavaScript we don't have interfaces, but we can use abstract classes
// or just follow a protocol by duck typing

class Publisher {
  constructor() {
    this.subscribers = new Set();
  }
  
  subscribe(subscriber) {
    this.subscribers.add(subscriber);
  }
  
  unsubscribe(subscriber) {
    this.subscribers.delete(subscriber);
  }
  
  publish(data) {
    for (const subscriber of this.subscribers) {
      subscriber.receive(this, data);
    }
  }
}

// NewsAgency example
class NewsAgency extends Publisher {
  constructor() {
    super();
    this._latestNews = null;
  }
  
  get latestNews() {
    return this._latestNews;
  }
  
  set latestNews(news) {
    this._latestNews = news;
    this.publish(news);
  }
}

class NewsChannel {
  constructor(name) {
    this.name = name;
    this.news = null;
  }
  
  receive(publisher, data) {
    this.news = data;
    console.log(`${this.name} received news: ${data}`);
  }
}

// Usage example
function runExamples() {
  // Example 1: Classic Observer pattern
  console.log("Example 1: Classic Observer Pattern");
  const weatherStation = new WeatherStation();
  const display = new TemperatureDisplay();
  const logger = new TemperatureLogger();
  
  weatherStation.attach(display);
  weatherStation.attach(logger);
  
  weatherStation.temperature = 25;
  weatherStation.temperature = 26;
  
  console.log("-".repeat(50));
  
  // Example 2: EventEmitter pattern
  console.log("Example 2: EventEmitter Pattern");
  const stockMarket = new StockMarket();
  
  function priceListener(newPrice, oldPrice) {
    console.log(`Stock price changed from ${oldPrice} to ${newPrice}`);
  }
  
  stockMarket.on('priceChanged', priceListener);
  
  stockMarket.price = 100;
  stockMarket.price = 101;
  
  console.log("-".repeat(50));
  
  // Example 3: Publisher-Subscriber pattern
  console.log("Example 3: Publisher-Subscriber Pattern");
  const agency = new NewsAgency();
  const channel1 = new NewsChannel("Channel 1");
  const channel2 = new NewsChannel("Channel 2");
  
  agency.subscribe(channel1);
  agency.subscribe(channel2);
  
  agency.latestNews = "Breaking News: JavaScript 2023 released!";
}

// Uncomment to run the examples
// runExamples();