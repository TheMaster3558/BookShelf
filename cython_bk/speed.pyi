from typing import Any, TypeVar, Optional, overload


KT = TypeVar('KT')
VT = TypeVar('VT')


@overload
def get_max(population: dict[KT, VT], greater_than: None) -> KT: ...

@overload
def get_max(population: dict[KT, VT], greater_than: Optional[Any]) -> Optional[KT]: ...

def get_max(population: dict[KT, VT], greater_than: Optional[Any] = None) -> Optional[KT]: ...
