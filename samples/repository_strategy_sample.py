"""
Sample implementation of the Repository-based Strategy pattern in Python.

The Repository-based Strategy pattern extends the traditional Strategy pattern
by centralizing the creation and management of strategy objects in a repository.
This provides a way to decouple strategy selection from strategy implementation
and enables runtime registration of new strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Type, Any


class SortStrategy(ABC):
    """Strategy interface for different sorting algorithms."""
    
    @abstractmethod
    def sort(self, data: List[int]) -> List[int]:
        """Sort the given data using a specific algorithm."""
        pass


class BubbleSortStrategy(SortStrategy):
    """Concrete strategy implementing bubble sort."""
    
    def sort(self, data: List[int]) -> List[int]:
        """Sort using bubble sort algorithm."""
        result = data.copy()
        n = len(result)
        for i in range(n):
            for j in range(0, n - i - 1):
                if result[j] > result[j + 1]:
                    result[j], result[j + 1] = result[j + 1], result[j]
        return result


class QuickSortStrategy(SortStrategy):
    """Concrete strategy implementing quick sort."""
    
    def sort(self, data: List[int]) -> List[int]:
        """Sort using quick sort algorithm."""
        result = data.copy()
        if len(result) <= 1:
            return result
        
        pivot = result[len(result) // 2]
        left = [x for x in result if x < pivot]
        middle = [x for x in result if x == pivot]
        right = [x for x in result if x > pivot]
        
        return self.sort(left) + middle + self.sort(right)


class MergeSortStrategy(SortStrategy):
    """Concrete strategy implementing merge sort."""
    
    def sort(self, data: List[int]) -> List[int]:
        """Sort using merge sort algorithm."""
        result = data.copy()
        if len(result) <= 1:
            return result
        
        # Split the list in half
        mid = len(result) // 2
        left = self.sort(result[:mid])
        right = self.sort(result[mid:])
        
        # Merge the sorted halves
        return self._merge(left, right)
    
    def _merge(self, left: List[int], right: List[int]) -> List[int]:
        """Merge two sorted lists."""
        merged = []
        i = j = 0
        
        # Compare elements from both lists and add the smaller one to the result
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        
        # Add any remaining elements
        merged.extend(left[i:])
        merged.extend(right[j:])
        
        return merged


class SortStrategyRepository:
    """Repository of sorting strategies."""
    
    # Dictionary to store available strategies
    _strategies = {}
    
    @classmethod
    def register(cls, key: str, strategy_class: Type[SortStrategy]) -> None:
        """Register a strategy with the repository.
        
        Args:
            key: Identifier for the strategy
            strategy_class: Strategy class to register
        """
        cls._strategies[key] = strategy_class
    
    @classmethod
    def get(cls, key: str) -> SortStrategy:
        """Get a strategy instance by key.
        
        Args:
            key: Identifier for the strategy
            
        Returns:
            Instance of the requested strategy
            
        Raises:
            KeyError: If the strategy key is not found
        """
        if key not in cls._strategies:
            raise KeyError(f"Strategy '{key}' not found in repository")
        
        return cls._strategies[key]()
    
    @classmethod
    def available_strategies(cls) -> List[str]:
        """Get a list of available strategy keys."""
        return list(cls._strategies.keys())


class Sorter:
    """Context that uses a strategy from the repository."""
    
    def __init__(self, strategy_type: str):
        """Initialize with a strategy type from the repository.
        
        Args:
            strategy_type: Key for the strategy in the repository
        """
        self._strategy_type = strategy_type
        self._strategy = SortStrategyRepository.get(strategy_type)
    
    @property
    def strategy_type(self) -> str:
        """Get the current strategy type."""
        return self._strategy_type
    
    @strategy_type.setter
    def strategy_type(self, strategy_type: str) -> None:
        """Change the strategy by selecting a new one from the repository.
        
        Args:
            strategy_type: Key for the new strategy in the repository
        """
        self._strategy_type = strategy_type
        self._strategy = SortStrategyRepository.get(strategy_type)
    
    def sort(self, data: List[int]) -> List[int]:
        """Sort the data using the current strategy."""
        return self._strategy.sort(data)


# Register strategies with the repository
SortStrategyRepository.register("bubble", BubbleSortStrategy)
SortStrategyRepository.register("quick", QuickSortStrategy)
SortStrategyRepository.register("merge", MergeSortStrategy)


# Dynamic strategy registration example
class HeapSortStrategy(SortStrategy):
    """Concrete strategy implementing heap sort."""
    
    def _heapify(self, arr: List[int], n: int, i: int) -> None:
        """Heapify subtree rooted at index i."""
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        if left < n and arr[i] < arr[left]:
            largest = left
            
        if right < n and arr[largest] < arr[right]:
            largest = right
            
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            self._heapify(arr, n, largest)
    
    def sort(self, data: List[int]) -> List[int]:
        """Sort using heap sort algorithm."""
        result = data.copy()
        n = len(result)
        
        # Build max heap
        for i in range(n // 2 - 1, -1, -1):
            self._heapify(result, n, i)
            
        # Extract elements one by one
        for i in range(n - 1, 0, -1):
            result[i], result[0] = result[0], result[i]
            self._heapify(result, i, 0)
            
        return result


# Register the new strategy at runtime
SortStrategyRepository.register("heap", HeapSortStrategy)


# Example of a generic data processor using the repository pattern
class ProcessingStrategy(ABC):
    """Strategy interface for data processing algorithms."""
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """Process the given data."""
        pass


class ProcessingStrategyRepository:
    """Repository of data processing strategies."""
    
    # Dictionary to store available strategies
    _strategies: Dict[str, Type[ProcessingStrategy]] = {}
    
    @classmethod
    def register(cls, key: str, strategy_class: Type[ProcessingStrategy]) -> None:
        """Register a strategy with the repository."""
        cls._strategies[key] = strategy_class
    
    @classmethod
    def get(cls, key: str) -> ProcessingStrategy:
        """Get a strategy instance by key."""
        if key not in cls._strategies:
            raise KeyError(f"Strategy '{key}' not found in repository")
        
        return cls._strategies[key]()


class DataProcessor:
    """Context that uses a processing strategy from the repository."""
    
    def __init__(self, strategy_type: str):
        """Initialize with a strategy type from the repository."""
        self._strategy_type = strategy_type
        self._strategy = ProcessingStrategyRepository.get(strategy_type)
    
    def process(self, data: Any) -> Any:
        """Process the data using the current strategy."""
        return self._strategy.process(data)


# Usage Example
if __name__ == "__main__":
    # Example data
    data = [7, 1, 5, 2, 4, 3, 6]
    
    # Create sorter with bubble sort strategy
    sorter = Sorter("bubble")
    print(f"Original data: {data}")
    print(f"Bubble sort: {sorter.sort(data)}")
    
    # Change strategy to quick sort
    sorter.strategy_type = "quick"
    print(f"Quick sort: {sorter.sort(data)}")
    
    # Change strategy to merge sort
    sorter.strategy_type = "merge"
    print(f"Merge sort: {sorter.sort(data)}")
    
    # Change strategy to heap sort (dynamically registered)
    sorter.strategy_type = "heap"
    print(f"Heap sort: {sorter.sort(data)}")
    
    # List all available strategies
    print(f"Available strategies: {SortStrategyRepository.available_strategies()}")