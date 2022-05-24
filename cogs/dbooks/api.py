import discord

import aiohttp


MISSING = discord.utils.MISSING


class DBooksClient:
    def __init__(self):
        self.session: aiohttp.ClientSession = MISSING

    async def cog_load(self) -> None:
        self.session = aiohttp.ClientSession(raise_for_status=True)

    async def cog_unload(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    async def search(self, query: str, *, result: int = 0) -> dict:
        async with self.session.get(f'https://www.dbooks.org/api/search/{query}') as resp:
            data = await resp.json()
        return data['books'][result]

