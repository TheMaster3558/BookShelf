import aiosqlite
import discord
from typing import Iterable


class ShareDatabase:
    def __init__(self):
        self.db: aiosqlite.Connection = aiosqlite.connect('./cogs/share/share.db')

    async def cog_load(self) -> None:
        await self.db

    async def cog_unload(self) -> None:
        await self.db.close()

    async def process_write(self, user: discord.abc.User, name: str, text: str) -> str:
        async with self.db.cursor() as cursor:
            await cursor.execute(
                f'''
                CREATE TABLE IF NOT EXISTS "{user.id}" (
                            name TEXT PRIMARY KEY,
                            text TEXT
                );
                '''
            )

            try:
                await cursor.execute(
                    f'''
                    INSERT INTO "{user.id}" VALUES (?, ?)
                    ''',
                    (name, text)
                )
            except aiosqlite.IntegrityError:
                return f'You already have a story named "{name}"'

        await self.db.commit()
        return f'Your writing has been saved!'

    async def fetch_writes(self, user: discord.abc.User) -> Iterable[tuple[str, str]]:
        async with self.db.cursor() as cursor:
            await cursor.execute(
                f'''
                SELECT * FROM "{user.id}";
                '''
            )
            return await cursor.fetchall()
