"""
Sample implementations of the Strategy pattern in Python.

The Strategy pattern defines a family of algorithms, encapsulates each one,
and makes them interchangeable. It lets the algorithm vary independently
from clients that use it.
"""

# Implementation 1: Classic Strategy Pattern with Context and Strategy interface

from abc import ABC, abstractmethod
from typing import List


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


class SortContext:
    """Context that uses a sort strategy."""
    
    def __init__(self, strategy: SortStrategy = None):
        """Initialize with an optional strategy."""
        self._strategy = strategy or BubbleSortStrategy()
    
    @property
    def strategy(self) -> SortStrategy:
        """Get the current strategy."""
        return self._strategy
    
    @strategy.setter
    def strategy(self, strategy: SortStrategy):
        """Set a new strategy."""
        self._strategy = strategy
    
    def sort(self, data: List[int]) -> List[int]:
        """Sort the data using the current strategy."""
        return self._strategy.sort(data)


# Implementation 2: Function-based Strategy Pattern

def bubble_sort(data: List[int]) -> List[int]:
    """Bubble sort implementation."""
    result = data.copy()
    n = len(result)
    for i in range(n):
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
    return result


def quick_sort(data: List[int]) -> List[int]:
    """Quick sort implementation."""
    result = data.copy()
    if len(result) <= 1:
        return result
    
    pivot = result[len(result) // 2]
    left = [x for x in result if x < pivot]
    middle = [x for x in result if x == pivot]
    right = [x for x in result if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)


def merge_sort(data: List[int]) -> List[int]:
    """Merge sort implementation."""
    result = data.copy()
    if len(result) <= 1:
        return result
    
    # Split the list in half
    mid = len(result) // 2
    left = merge_sort(result[:mid])
    right = merge_sort(result[mid:])
    
    # Merge the sorted halves
    return _merge(left, right)


def _merge(left: List[int], right: List[int]) -> List[int]:
    """Helper function to merge two sorted lists."""
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


class FunctionalSortContext:
    """Context that uses a sorting function as a strategy."""
    
    def __init__(self, strategy = bubble_sort):
        """Initialize with a sort function (strategy)."""
        self._strategy = strategy
    
    @property
    def strategy(self):
        """Get the current strategy function."""
        return self._strategy
    
    @strategy.setter
    def strategy(self, strategy):
        """Set a new strategy function."""
        self._strategy = strategy
    
    def sort(self, data: List[int]) -> List[int]:
        """Sort the data using the current strategy function."""
        return self._strategy(data)


# Implementation 3: Dictionary-based Strategy Pattern

class PaymentProcessor:
    """Context that processes payments using different strategies."""
    
    # Dictionary of available payment strategies
    STRATEGIES = {
        'credit_card': lambda amount: f"Processing credit card payment of ${amount}",
        'paypal': lambda amount: f"Processing PayPal payment of ${amount}",
        'bank_transfer': lambda amount: f"Processing bank transfer of ${amount}",
        'cryptocurrency': lambda amount: f"Processing cryptocurrency payment of ${amount}",
    }
    
    def __init__(self, strategy='credit_card'):
        """Initialize with a payment strategy."""
        if strategy not in self.STRATEGIES:
            raise ValueError(f"Unknown payment strategy: {strategy}")
        self._strategy = strategy
    
    @property
    def strategy(self):
        """Get the current payment strategy."""
        return self._strategy
    
    @strategy.setter
    def strategy(self, strategy):
        """Set a new payment strategy."""
        if strategy not in self.STRATEGIES:
            raise ValueError(f"Unknown payment strategy: {strategy}")
        self._strategy = strategy
    
    def process_payment(self, amount):
        """Process a payment using the current strategy."""
        return self.STRATEGIES[self._strategy](amount)


# Usage Example
if __name__ == "__main__":
    # Example 1: Class-based Strategy Pattern
    print("Example 1: Class-based Strategy Pattern")
    data = [7, 1, 5, 2, 4, 3, 6]
    
    context = SortContext()
    print(f"Original data: {data}")
    print(f"Bubble sort: {context.sort(data)}")
    
    context.strategy = QuickSortStrategy()
    print(f"Quick sort: {context.sort(data)}")
    
    context.strategy = MergeSortStrategy()
    print(f"Merge sort: {context.sort(data)}")
    
    print("-" * 50)
    
    # Example 2: Function-based Strategy Pattern
    print("Example 2: Function-based Strategy Pattern")
    
    func_context = FunctionalSortContext()
    print(f"Original data: {data}")
    print(f"Bubble sort: {func_context.sort(data)}")
    
    func_context.strategy = quick_sort
    print(f"Quick sort: {func_context.sort(data)}")
    
    func_context.strategy = merge_sort
    print(f"Merge sort: {func_context.sort(data)}")
    
    print("-" * 50)
    
    # Example 3: Dictionary-based Strategy Pattern
    print("Example 3: Dictionary-based Strategy Pattern")
    
    payment = PaymentProcessor()
    print(payment.process_payment(100))
    
    payment.strategy = 'paypal'
    print(payment.process_payment(100))
    
    payment.strategy = 'bank_transfer'
    print(payment.process_payment(100))
    
    payment.strategy = 'cryptocurrency'
    print(payment.process_payment(100))