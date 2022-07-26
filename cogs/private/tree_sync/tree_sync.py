from __future__ import annotations

import json
from typing import TYPE_CHECKING

import aiofiles
import discord
from discord.ext import commands

if TYPE_CHECKING:
    from bot import BookShelf


class TreeSync(commands.Cog):
    def __init__(self, bot: BookShelf):
        self.bot = bot

    def app_commands_to_list(self) -> list[dict]:
        return [command.to_dict() for command in self.bot.tree.get_commands()]

    async def write_app_commands(self) -> None:
        data = self.app_commands_to_list()
        dumped = json.dumps(data, indent=4)

        async with aiofiles.open('./cogs/private/tree_sync/app_commands.json', 'w') as file:
            await file.write(dumped)

    async def get_app_commands(self) -> list[dict]:
        async with aiofiles.open('./cogs/private/tree_sync/app_commands.json', 'r') as file:
            raw = await file.read()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            await self.write_app_commands()
            return await self.get_app_commands()

        return data

    async def check_if_should_sync(self) -> bool:
        return self.app_commands_to_list() != await self.get_app_commands()

    async def sync(self):
        await self.bot.wait_until_ready()
        if await self.check_if_should_sync():
            await self.bot.tree.sync()
            await self.write_app_commands()

    async def cog_load(self) -> None:
        self.bot.loop.create_task(self.sync())

    @commands.command(
        name='sync',
        description='Sync app commands!'
    )
    @commands.is_owner()
    async def message_sync(self, ctx: commands.Context, test_guild: bool = False):
        try:
            if test_guild:
                await self.bot.tree.sync(guild=self.bot.test_guild)
            else:
                await self.bot.tree.sync()
        except discord.HTTPException as exc:
            await ctx.send(f'There was an error while syncing. \n```\n{exc}\n```')
        else:
            await ctx.send('Successfully synced.')
