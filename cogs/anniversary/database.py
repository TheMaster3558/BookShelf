from typing import Iterable

import aiosqlite
import discord


MISSING = discord.utils.MISSING


class AnniversaryDatabase:
    def __init__(self):
        self.db: aiosqlite.Connection = aiosqlite.connect('./cogs/anniversary/anniversary.db')

    async def cog_load(self) -> None:
        await self.db
        async with self.db.cursor() as cursor:
            await cursor.execute(
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

    async def add_year(self, user: discord.User, year: int) -> None:
        async with self.db.cursor() as cursor:
            try:
                await cursor.execute(
                    '''
                    INSERT INTO "anniversaries" VALUES (?, ?);
                    ''',
                    (user.id, year)
                )
            except aiosqlite.IntegrityError:
                await cursor.execute(
                    '''
                    UPDATE "anniversaries"
                    SET user_id = ?, year = ?
                    WHERE user_id = ?;
                    ''',
                    (user.id, year, user.id)
                )
        await self.db.commit()

    async def get_all_users(self) -> Iterable[tuple[int, int]]:
        async with self.db.cursor() as cursor:
            await cursor.execute(
                '''
                SELECT * FROM "anniversaries";
                '''
            )
            return await cursor.fetchall()
