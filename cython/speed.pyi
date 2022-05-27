from typing import TypeVar


K = TypeVar('K')
V = TypeVar('V')


def get_max(population: dict[K, V]) -> K: ...
