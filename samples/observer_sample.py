"""
Sample implementations of the Observer pattern in Python.

The Observer pattern defines a one-to-many dependency between objects so that
when one object changes state, all its dependents are notified and updated
automatically.
"""

# Implementation 1: Classic Observer Pattern with Subject and Observer base classes

class Subject:
    """Base Subject class for the Observer pattern."""
    
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        """Attach an observer to the subject."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer):
        """Detach an observer from the subject."""
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
    
    def notify(self):
        """Notify all observers about an event."""
        for observer in self._observers:
            observer.update(self)


class Observer:
    """Base Observer class for the Observer pattern."""
    
    def update(self, subject):
        """Receive update from subject."""
        raise NotImplementedError("Observers must implement update method")


# Concrete implementation of the Observer pattern

class WeatherStation(Subject):
    """Example concrete subject: weather station that measures temperature."""
    
    def __init__(self):
        super().__init__()
        self._temperature = 0
    
    @property
    def temperature(self):
        return self._temperature
    
    @temperature.setter
    def temperature(self, value):
        """Set temperature and notify observers if changed."""
        if self._temperature != value:
            self._temperature = value
            self.notify()


class TemperatureDisplay(Observer):
    """Display that shows the current temperature."""
    
    def update(self, subject):
        print(f"Temperature Display: {subject.temperature}°C")


class TemperatureLogger(Observer):
    """Logger that records temperature changes."""
    
    def __init__(self):
        self.log = []
    
    def update(self, subject):
        self.log.append(subject.temperature)
        print(f"Temperature Logger: Recorded {subject.temperature}°C")


# Implementation 2: Observer pattern using functions and callbacks

class EventEmitter:
    """Subject implementation using callbacks."""
    
    def __init__(self):
        self._callbacks = {}
    
    def on(self, event_name, callback):
        """Subscribe to an event."""
        if event_name not in self._callbacks:
            self._callbacks[event_name] = []
        self._callbacks[event_name].append(callback)
    
    def off(self, event_name, callback):
        """Unsubscribe from an event."""
        if event_name in self._callbacks:
            try:
                self._callbacks[event_name].remove(callback)
            except ValueError:
                pass
    
    def emit(self, event_name, *args, **kwargs):
        """Emit an event with data."""
        if event_name in self._callbacks:
            for callback in self._callbacks[event_name]:
                callback(*args, **kwargs)


# Example usage of the functional implementation

class StockMarket(EventEmitter):
    """Example using the EventEmitter implementation."""
    
    def __init__(self):
        super().__init__()
        self._price = 0
    
    @property
    def price(self):
        return self._price
    
    @price.setter
    def price(self, value):
        if self._price != value:
            old_price = self._price
            self._price = value
            self.emit('price_changed', value, old_price)


# Implementation 3: Observer pattern with protocol/interface

from abc import ABC, abstractmethod

class Publisher(ABC):
    """Abstract publisher interface."""
    
    @abstractmethod
    def subscribe(self, subscriber):
        pass
    
    @abstractmethod
    def unsubscribe(self, subscriber):
        pass
    
    @abstractmethod
    def publish(self):
        pass


class Subscriber(ABC):
    """Abstract subscriber interface."""
    
    @abstractmethod
    def receive(self, publisher, data):
        pass


class NewsAgency(Publisher):
    """Concrete publisher implementation."""
    
    def __init__(self):
        self._subscribers = set()
        self._latest_news = None
    
    def subscribe(self, subscriber):
        self._subscribers.add(subscriber)
    
    def unsubscribe(self, subscriber):
        self._subscribers.discard(subscriber)
    
    def publish(self):
        for subscriber in self._subscribers:
            subscriber.receive(self, self._latest_news)
    
    @property
    def latest_news(self):
        return self._latest_news
    
    @latest_news.setter
    def latest_news(self, news):
        self._latest_news = news
        self.publish()


class NewsChannel(Subscriber):
    """Concrete subscriber implementation."""
    
    def __init__(self, name):
        self.name = name
        self.news = None
    
    def receive(self, publisher, data):
        self.news = data
        print(f"{self.name} received news: {data}")


# Usage example
if __name__ == "__main__":
    # Example 1: Classic Observer pattern
    print("Example 1: Classic Observer Pattern")
    weather_station = WeatherStation()
    display = TemperatureDisplay()
    logger = TemperatureLogger()
    
    weather_station.attach(display)
    weather_station.attach(logger)
    
    weather_station.temperature = 25
    weather_station.temperature = 26
    
    print("-" * 50)
    
    # Example 2: Functional Observer pattern
    print("Example 2: Functional Observer Pattern")
    stock_market = StockMarket()
    
    def price_listener(new_price, old_price):
        print(f"Stock price changed from {old_price} to {new_price}")
    
    stock_market.on('price_changed', price_listener)
    
    stock_market.price = 100
    stock_market.price = 101
    
    print("-" * 50)
    
    # Example 3: Publisher-Subscriber pattern
    print("Example 3: Publisher-Subscriber Pattern")
    agency = NewsAgency()
    channel1 = NewsChannel("Channel 1")
    channel2 = NewsChannel("Channel 2")
    
    agency.subscribe(channel1)
    agency.subscribe(channel2)
    
    agency.latest_news = "Breaking News: Python 4.0 released!"