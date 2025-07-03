"""Strategy pattern example for sorting data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List
import timeit


class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: List[int]) -> List[int]: ...


class AscendingSort(SortStrategy):
    def sort(self, data: List[int]) -> List[int]:
        return sorted(data)


class DescendingSort(SortStrategy):
    def sort(self, data: List[int]) -> List[int]:
        return sorted(data, reverse=True)


class Sorter:
    def __init__(self, strategy: SortStrategy) -> None:
        self.strategy = strategy

    def execute_sort(self, data: List[int]) -> List[int]:
        return self.strategy.sort(data)


if __name__ == "__main__":
    numbers = list(range(1000, 0, -1))
    sorter = Sorter(AscendingSort())
    asc_time = timeit.timeit(lambda: sorter.execute_sort(numbers), number=100)
    sorter.strategy = DescendingSort()
    desc_time = timeit.timeit(lambda: sorter.execute_sort(numbers), number=100)
    print(f"Ascending: {asc_time:.4f}s, Descending: {desc_time:.4f}s")
