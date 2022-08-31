import aiosqlite
import discord


class Database:
    def __init__(self):
        self.db: aiosqlite.Connection = aiosqlite.connect('./cogs/nasa/channels.db')

    async def cog_load(self):
        await self.db
        async with self.db.cursor() as cursor:
            await cursor.execute(
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
        async with self.db.cursor() as cursor:
            try:
                await cursor.execute(
                    '''
                    INSERT INTO "channels" VALUES (?, ?);
                    ''',
                    (channel.guild.id, channel.id)
                )
            except aiosqlite.IntegrityError:
                await cursor.execute(
                    '''
                    UPDATE "channels" 
                    SET channel_id = ?
                    WHERE guild_id = ?;
                    ''',
                    (channel.id, channel.guild.id)
                )
        await self.db.commit()

    async def delete_channel(self, guild: discord.Guild) -> None:
        async with self.db.cursor() as cursor:
            await cursor.execute(
                '''
                DELETE FROM "channels"
                WHERE guild_id = ?;
                ''',
                (guild.id,)
            )
        await self.db.commit()

    async def get_channels(self):
        async with self.db.cursor() as cursor:
            await cursor.execute(
                '''
                SELECT channel_id FROM "channels";
                '''
            )
            return await cursor.fetchall()
