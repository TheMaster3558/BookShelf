import datetime
import json

import aiofiles
import discord


class EmbedStorage:
    conversion: dict[type, str] = {
        discord.User: 'user',
        discord.Member: 'member',
        discord.Guild: 'guild',
        discord.Role: 'role'
    }

    def __init__(self):
        self.data: dict[str, list[discord.Embed]] = {}

    def insert(self, id: int, embed: discord.Embed, type: str) -> None:
        key = f'{id}_{type}'
        if key not in self.data:
            self.data[key] = []

        self.data[key].append(embed)

    def get(self, obj: discord.abc.Snowflake, date: datetime.datetime = None) -> discord.Embed | None:  # type: ignore
        if not date:
            return None

        key = f'{obj.id}_{self.conversion[type(obj)]}'
        embeds = self.data.get(key)
        if not embeds:
            return None

        for embed in embeds:
            if not embed.timestamp:
                continue
            if embed.timestamp.day == date.day:
                return embed

    async def cog_load(self):
        await self.from_file()

    async def cog_unload(self):
        await self.to_file()

    async def to_file(self):
        data = {id: [embed.to_dict() for embed in embeds] for id, embeds in self.data.items()}
        dumped = json.dumps(data, indent=4)

        async with aiofiles.open('./cogs/info/embed_storage.json', 'w') as file:
            await file.write(dumped)

    async def from_file(self):
        async with aiofiles.open('./cogs/info/embed_storage.json', 'r') as file:
            raw = await file.read()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            async with aiofiles.open('./cogs/info/embed_storage.json', 'w') as file:
                await file.write('{}')
            return await self.from_file()

        for id, embeds in data.items():

            self.data[id] = [discord.Embed.from_dict(embed) for embed in embeds]
