from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from bot import BookShelf


class DBooksClient:
    bot: BookShelf

    BASE: ClassVar[str] = 'https://www.dbooks.org/api'

    async def search(self, query: str, *, result: int = 0) -> dict:
        async with self.bot.session.get(f'{self.BASE}/search/{query}') as resp:
            data = await resp.json()
        return data['books'][result]

