from typing import TypeVar


KT = TypeVar('KT')
VT = TypeVar('VT')


def get_max(population: dict[KT, VT]) -> KT: ...
