"""
Sample implementations of the Facade pattern in Python.

The Facade pattern provides a simplified interface to a complex subsystem.
It doesn't encapsulate the subsystem but provides a unified interface to make
the subsystem easier to use.
"""

# Implementation 1: Classic Facade Pattern


class ComplexSubsystemA:
    """A complex subsystem component."""
    
    def operation1(self) -> str:
        return "Subsystem A: Operation 1"
    
    def operation2(self) -> str:
        return "Subsystem A: Operation 2"


class ComplexSubsystemB:
    """Another complex subsystem component."""
    
    def operation1(self) -> str:
        return "Subsystem B: Operation 1"
    
    def operation2(self) -> str:
        return "Subsystem B: Operation 2"


class ComplexSubsystemC:
    """Yet another complex subsystem component."""
    
    def operation1(self) -> str:
        return "Subsystem C: Operation 1"


class Facade:
    """Facade provides a simple interface to the complex subsystem."""
    
    def __init__(self):
        """Initialize the facade with subsystem objects."""
        self._subsystem_a = ComplexSubsystemA()
        self._subsystem_b = ComplexSubsystemB()
        self._subsystem_c = ComplexSubsystemC()
    
    def operation(self) -> str:
        """
        The facade method that provides a simplified interface.
        It delegates to subsystem objects to perform complex operations.
        """
        results = []
        results.append("Facade initializes subsystems:")
        results.append(self._subsystem_a.operation1())
        results.append(self._subsystem_b.operation1())
        results.append("Facade orders subsystems to perform the action:")
        results.append(self._subsystem_a.operation2())
        results.append(self._subsystem_b.operation2())
        results.append(self._subsystem_c.operation1())
        return "\n".join(results)


# Implementation 2: Facade with Configuration


class DatabaseService:
    """Database service for complex database operations."""
    
    def connect(self, connection_string):
        return f"Connected to database with {connection_string}"
    
    def execute_query(self, query):
        return f"Executing query: {query}"
    
    def close_connection(self):
        return "Database connection closed"


class CacheService:
    """Cache service for handling caching operations."""
    
    def get(self, key):
        return f"Getting {key} from cache"
    
    def set(self, key, value):
        return f"Setting {key}={value} in cache"
    
    def clear(self):
        return "Clearing cache"


class LogService:
    """Logging service for various log levels."""
    
    def info(self, message):
        return f"INFO: {message}"
    
    def error(self, message):
        return f"ERROR: {message}"
    
    def debug(self, message):
        return f"DEBUG: {message}"


class DataServiceFacade:
    """
    Facade that provides a simplified interface to database, cache, and logging services.
    """
    
    def __init__(self, db_connection_string):
        """Initialize the facade with the provided configuration."""
        self.db = DatabaseService()
        self.cache = CacheService()
        self.logger = LogService()
        self.connection_string = db_connection_string
    
    def get_data(self, key, query):
        """Get data first checking cache, then falling back to database query."""
        # Log operation
        self.logger.info(f"Getting data for {key}")
        
        # Try from cache first
        cache_result = self.cache.get(key)
        self.logger.debug(f"Cache result: {cache_result}")
        
        # If not in cache, get from database
        self.logger.info("Getting data from database")
        self.db.connect(self.connection_string)
        db_result = self.db.execute_query(query)
        self.db.close_connection()
        
        # Update cache
        self.cache.set(key, "result_from_query")
        
        return f"Data retrieved for {key}"
    
    def clear_cache(self):
        """Clear the cache and log the operation."""
        self.logger.info("Clearing all cache")
        result = self.cache.clear()
        return result


# Implementation 3: Module-level Facade


# These would normally be in separate modules
def _complex_algorithm_part1(data):
    return f"Processing {data} with algorithm part 1"


def _complex_algorithm_part2(data):
    return f"Processing {data} with algorithm part 2"


def _format_result(result):
    return f"Formatted: {result}"


# Facade function that simplifies the algorithm usage
def process_data(data):
    """
    A function facade that simplifies the usage of a complex algorithm.
    """
    # Step 1: Run first part of algorithm
    intermediate_result = _complex_algorithm_part1(data)
    
    # Step 2: Run second part of algorithm
    final_result = _complex_algorithm_part2(intermediate_result)
    
    # Step 3: Format the result
    formatted_result = _format_result(final_result)
    
    return formatted_result


# Usage Example
if __name__ == "__main__":
    # Example 1: Classic Facade
    print("Example 1: Classic Facade")
    facade = Facade()
    result = facade.operation()
    print(result)
    
    print("-" * 50)
    
    # Example 2: Configurable Facade
    print("Example 2: Configurable Facade")
    data_service = DataServiceFacade("mysql://localhost:3306/mydatabase")
    result = data_service.get_data("user:123", "SELECT * FROM users WHERE id=123")
    print(result)
    result = data_service.clear_cache()
    print(result)
    
    print("-" * 50)
    
    # Example 3: Function Facade
    print("Example 3: Function Facade")
    result = process_data("raw_data")
    print(result)