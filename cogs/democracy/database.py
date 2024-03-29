from typing import Iterable, Optional, Sequence

from datetime import datetime, timedelta

import aiosqlite
import discord


class DemocracyDatabase:
    def __init__(self):
        self.db: aiosqlite.Connection = aiosqlite.connect('./cogs/democracy/democracy.db')

    async def cog_load(self) -> None:
        await self.db
        async with self.db.cursor() as cursor:
            await cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS "elections" (
                            guild_id INT PRIMARY KEY,
                            expiry TEXT,
                            channel_id INT
                );
                '''
            )
        await self.db.commit()

    async def cog_unload(self) -> None:
        await self.db.close()

    async def create_election(self, guild: discord.Guild, expiry: int, channel: discord.TextChannel) -> str:
        expiry: datetime = discord.utils.utcnow() + timedelta(days=expiry)

        async with self.db.cursor() as cursor:
            try:
                await cursor.execute(
                    f'''
                    CREATE TABLE "votes_{guild.id}" (
                                member_id INT PRIMARY KEY,
                                who INT
                    );
                    '''
                )

                await cursor.execute(
                    '''
                    INSERT INTO "elections" VALUES (?, ?, ?);
                    ''',
                    (guild.id, expiry.isoformat(), channel.id)
                )
            except aiosqlite.IntegrityError:
                return 'There is already an election running in this server.'

        await self.db.commit()
        return 'Election successfully created!'

    async def user_vote(self, member: discord.Member,
                        who: discord.Member) -> bool:
        updated = False

        async with self.db.cursor() as cursor:
            try:
                await cursor.execute(
                    f'''
                    INSERT INTO "votes_{member.guild.id}" VALUES (?, ?);
                    ''',
                    (member.id, who.id)
                )
            except aiosqlite.IntegrityError:
                await cursor.execute(
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

    async def finish_election(self, guild: discord.Guild) -> Iterable[tuple[int, int]]:
        async with self.db.cursor() as cursor:
            await cursor.execute(
                f'''
                SELECT who FROM "votes_{guild.id}";
                '''
            )
            results = await cursor.fetchall()

            await cursor.execute(
                f'''
                DROP TABLE "votes_{guild.id}";
                '''
            )

            await cursor.execute(
                '''
                DELETE FROM "elections"
                WHERE guild_id = ?;
                ''',
                (guild.id,)
            )

        await self.db.commit()
        return results

    async def get_end(self, guild: Optional[discord.Guild] = None) -> Sequence[tuple[int, str, int]]:
        sql = '''
        SELECT channel_id FROM "elections"
        '''
        if guild:
            sql += f'''
            WHERE guild_id = {guild.id}
            '''

        async with self.db.cursor() as cursor:
            await cursor.execute(sql)
            return await cursor.fetchall()
