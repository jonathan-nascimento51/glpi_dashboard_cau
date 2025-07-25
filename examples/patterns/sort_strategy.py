"""Strategy pattern example for sorting data."""

from __future__ import annotations

import timeit
from abc import ABC, abstractmethod
from typing import List

from shared.utils.logging import get_logger


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
    logger = get_logger(__name__)

    numbers = list(range(1000, 0, -1))
    sorter = Sorter(AscendingSort())
    asc_time = timeit.timeit(lambda: sorter.execute_sort(numbers), number=100)
    sorter.strategy = DescendingSort()
    desc_time = timeit.timeit(lambda: sorter.execute_sort(numbers), number=100)
    logger.info(
        "Ascending: %.4fs, Descending: %.4fs",
        asc_time,
        desc_time,
    )
