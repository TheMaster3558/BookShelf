import aiosqlite
import discord
from typing import Iterable


MISSING = discord.utils.MISSING


class ShareDatabase:
    def __init__(self):
        self.db: aiosqlite.Connection = MISSING

    async def cog_load(self) -> None:
        self.db = await aiosqlite.connect('./cogs/share/share.db')

    async def cog_unload(self) -> None:
        await self.db.close()

    async def process_write(self, user: discord.Member | discord.User, name: str, text: str) -> str:
        await self.db.execute(
            f'''
            CREATE TABLE IF NOT EXISTS "{user.id}" (
                        name TEXT PRIMARY KEY,
                        text TEXT
            );
            '''
        )

        try:
            await self.db.execute(
                f'''
                INSERT INTO "{user.id}" VALUES (?, ?)
                ''',
                (name, text)
            )
            await self.db.commit()
        except aiosqlite.IntegrityError:
            return f'You already have a story named "{name}"'
        return f'Your writing has been saved!'

    async def fetch_writes(self, user: discord.Member | discord.User) -> Iterable[tuple[str, str]]:
        async with self.db.execute(
                f'''
            SELECT * FROM "{user.id}"
            '''
        ) as cursor:
            return await cursor.fetchall()
