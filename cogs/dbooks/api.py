from __future__ import annotations

from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from bot import BookShelf


MISSING = discord.utils.MISSING


class DBooksClient:
    bot: BookShelf

    async def search(self, query: str, *, result: int = 0) -> dict:
        async with self.bot.session.get(f'https://www.dbooks.org/api/search/{query}') as resp:
            data = await resp.json()
        return data['books'][result]

