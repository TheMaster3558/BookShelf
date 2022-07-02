import aiosqlite
import discord


MISSING = discord.utils.MISSING


class Database:
    def __init__(self):
        self.db: aiosqlite.Connection = MISSING

    async def cog_load(self):
        self.db = await aiosqlite.connect('./cogs/nasa/channels.db')
        await self.db.execute(
            '''
            CREATE TABLE IF NOT EXISTS "channels" (
                        guild_id INT PRIMARY KEY,
                        channel_id INT
            );
            '''
        )
        await self.db.commit()

    async def cog_unload(self):
        await self.db.close()

    async def add_channel(self, channel: discord.abc.GuildChannel) -> None:
        try:
            await self.db.execute(
                '''
                INSERT INTO "channels" VALUES (?, ?);
                ''',
                (channel.guild.id, channel.id)
            )
        except aiosqlite.IntegrityError:
            await self.db.execute(
                '''
                UPDATE "channels" 
                SET channel_id = ?
                WHERE guild_id = ?;
                ''',
                (channel.id, channel.guild.id)
            )
        await self.db.commit()

    async def delete_channel(self, guild: discord.Guild) -> None:
        await self.db.execute(
            '''
            DELETE FROM "channels"
            WHERE guild_id = ?;
            ''',
            (guild.id,)
        )

    async def get_channels(self):
        async with self.db.execute(
            '''
            SELECT channel_id FROM "channels";
            '''
        ) as cursor:
            return await cursor.fetchall()
