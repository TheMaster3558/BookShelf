import aiosqlite
import discord


MISSING = discord.utils.MISSING


class ShareDatabase:
    def __init__(self):
        self.db: aiosqlite.Connection = MISSING

    async def cog_load(self) -> None:
        self.db = await aiosqlite.connect('./cogs/share/share.db')

    async def cog_unload(self) -> None:
        await self.db.close()

    async def process_write(self, username: str, name: str, text: str) -> str:
        await self.db.execute(
            f'''
            CREATE TABLE IF NOT EXISTS "{username}" (
                        name TEXT PRIMARY KEY,
                        text TEXT
            );
            '''
        )

        try:
            await self.db.execute(
                f'''
                INSERT INTO "{username}" VALUES (?, ?)
                ''',
                (name, text)
            )
            await self.db.commit()
        except aiosqlite.IntegrityError:
            return f'You already have a story named "{name}"'
        return f'Your writing has been saved!'

    async def fetch_writes(self, username: str):
        async with self.db.execute(
                f'''
            SELECT * FROM "{username}"
            '''
        ) as cursor:
            return await cursor.fetchall()
