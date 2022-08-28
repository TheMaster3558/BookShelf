import json
from typing import Optional

import aiofiles
import aiosqlite
import discord


class RolesDatabase:
    def __init__(self):
        self.db = aiosqlite.connect('./cogs/roles/database.db')
        self.messages: list[int] = []

    async def from_file(self) -> None:
        async with aiofiles.open('./cogs/roles/messages.json', 'r') as file:
            raw = await file.read()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            async with aiofiles.open('./cogs/roles/messages.json', 'w') as file:
                await file.write('[]')
                return await self.from_file()

        self.messages = data

    async def to_file(self) -> None:
        dumped = json.dumps(self.messages)

        async with aiofiles.open('./cogs/roles/messages.json', 'w') as file:
            await file.write(dumped)

    async def cog_load(self) -> None:
        await self.from_file()
        await self.db
        await self.db.execute(
            '''
            CREATE TABLE IF NOT EXISTS "authors" (
                    message_id INT PRIMARY KEY,
                    author_id INT
            );
            '''
        )
        await self.db.commit()

    async def cog_unload(self) -> None:
        await self.to_file()
        await self.db.close()

    async def insert(
            self,
            roles: list[str],
            descriptions: list[Optional[str]],
            emojis: list[discord.PartialEmoji],
            author: discord.Member,
            message: discord.Message,
            updating: bool = False
    ) -> None:
        await self.db.execute(
            f'''
            CREATE TABLE "{message.id}" (
                    role TEXT PRIMARY KEY,
                    description TEXT,
                    emoji TEXT
            );
            '''
        )

        for role, description, emoji in zip(roles, descriptions, emojis):
            await self.db.execute(
                f'''
                INSERT INTO "{message.id}" VALUES (?, ?, ?);
                ''',
                (role, description or '', str(emoji.id or emoji.name if emoji else emoji))
            )

        if not updating:
            await self.db.execute(
                '''
                INSERT INTO "authors" VALUES (?, ?);
                ''',
                (message.id, author.id)
            )
        await self.db.commit()

    async def delete(self, message: discord.Message) -> None:
        await self.db.execute(
            f'''
            DROP TABLE "{message.id}";
            '''
        )
        await self.db.commit()

    async def get_roles(self, message: discord.Message) -> list[tuple[str, str, str]]:
        async with self.db.execute(
            f'''
            SELECT * FROM "{message.id}";
            '''
        ) as cursor:
            return await cursor.fetchall()

    async def get_author(self, message: discord.Message) -> int:
        async with self.db.execute(
            '''
            SELECT author_id FROM "authors"
            WHERE message_id = ?;
            ''',
            (message.id,)
        ) as cursor:
            return (await cursor.fetchone())[0]
