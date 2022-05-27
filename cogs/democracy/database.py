from typing import Optional

from datetime import datetime, timedelta

import aiosqlite
import discord


MISSING = discord.utils.MISSING


class DemocracyDatabase:
    def __init__(self):
        self.db: aiosqlite.Connection = MISSING

    async def cog_load(self) -> None:
        self.db = await aiosqlite.connect('./cogs/democracy/democracy.db')

        await self.db.execute(
            '''
            CREATE TABLE IF NOT EXISTS "elections" (
                        guild_id INT PRIMARY KEY,
                        expiry TEXT,
                        channel_id INT
            );
            '''
        )

    async def cog_unload(self) -> None:
        await self.db.close()

    async def create_election(self, guild: discord.Guild, expiry: int, channel: discord.TextChannel) -> str:
        expiry: datetime = discord.utils.utcnow() + timedelta(days=expiry)  # type: ignore

        try:
            await self.db.execute(
                f'''
                CREATE TABLE "votes_{guild.id}" (
                            member_id INT PRIMARY KEY,
                            who INT
                );
                '''
            )

            await self.db.execute(
                '''
                INSERT INTO "elections" VALUES (?, ?, ?);
                ''',
                (guild.id, expiry.isoformat(), channel.id)  # type: ignore
            )
        except aiosqlite.IntegrityError:
            return 'There is already an election running in this server.'
        return 'Election successfully created!'

    async def user_vote(self, member: discord.Member,
                        who: discord.Member) -> bool:
        updated = False
        try:
            await self.db.execute(
                f'''
                INSERT INTO "votes_{member.guild.id}" VALUES (?, ?);
                ''',
                (member.id, who.id)
            )
        except aiosqlite.IntegrityError:
            await self.db.execute(
                f'''
                UPDATE "votes_{member.guild.id}"
                SET member_id = ?, who = ?
                WHERE member_id = ?;
                ''',
                (member.id, who.id, member.id)
            )
            updated = True

        await self.db.commit()

        return updated

    async def finish_election(self, guild: discord.Guild):
        async with self.db.execute(
            f'''
            SELECT who FROM "votes_{guild.id}";
            '''
        ) as cursor:
            results = await cursor.fetchall()

        await self.db.execute(
            f'''
            DROP TABLE "votes_{guild.id}";
            '''
        )

        await self.db.execute(
            '''
            DELETE FROM "elections"
            WHERE guild_id = ?;
            ''',
            (guild.id,)
        )

        await self.db.commit()

        return results

    async def get_end(self, guild: Optional[discord.Guild] = None):
        sql = '''
        SELECT * FROM "elections"
        '''
        if guild:
            sql += f'''
            WHERE guild_id = {guild.id}
            '''

        async with self.db.execute(
            sql
        ) as cursor:
            return await cursor.fetchall()
