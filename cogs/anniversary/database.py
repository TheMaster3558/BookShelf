from typing import Iterable

import aiosqlite
import discord


MISSING = discord.utils.MISSING


class AnniversaryDatabase:
    def __init__(self):
        self.db: aiosqlite.Connection = MISSING

    async def cog_load(self) -> None:
        self.db = await aiosqlite.connect('./cogs/anniversary/anniversary.db')

        await self.db.execute(
            '''
            CREATE TABLE IF NOT EXISTS "anniversaries" (
                        user_id INT PRIMARY KEY,
                        year INT
            );
            '''
        )
        await self.db.commit()

    async def cog_unload(self) -> None:
        await self.db.close()

    async def add_year(self, user: discord.abc.Snowflake, year: int) -> None:
        try:
            await self.db.execute(
                '''
                INSERT INTO "anniversaries" VALUES (?, ?)
                ''',
                (user.id, year)
            )
        except aiosqlite.IntegrityError:
            await self.db.execute(
                '''
                UPDATE "anniversaries"
                SET user_id = ?, year = ?
                WHERE user_id = ?;
                ''',
                (user.id, year, user.id)
            )

        await self.db.commit()

    async def get_all_users(self) -> Iterable[tuple[int, int]]:
        async with self.db.execute(
            '''
            SELECT * FROM "anniversaries";
            '''
        ) as cursor:
            return await cursor.fetchall()


