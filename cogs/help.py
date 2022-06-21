from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Sequence

import discord
from discord.ext import commands

from utils import split_embeds

if TYPE_CHECKING:
    from bot import BookShelf


class HelpCommand(commands.HelpCommand):
    async def send(
            self,
            embed: Optional[discord.Embed] = None,
            embeds: Sequence[discord.Embed] = (),
            channel: Optional[discord.abc.Messageable] = None
    ):
        embeds = list(embeds)

        if channel is None:
            channel = self.get_destination()

        if embed:
            embeds.append(embed)

        await split_embeds(embeds, channel)

    async def send_bot_help(self, mapping: dict) -> None:
        embeds = []

        for cog, cmds in mapping.items():
            embed = None

            if cog and cmds:
                embed = self.get_cog_embed(cog)

            if embed:
                embeds.append(embed)

        await self.send(embeds=embeds, channel=self.context.author)

    def get_command_embed(self, command: commands.Command) -> discord.Embed:
        embed = discord.Embed(
            title=command.qualified_name,
            description=command.description
        )
        embed.add_field(
            name='Usage',
            value=f'```{self.get_command_signature(command)}```'
        )

        return embed

    async def send_command_help(self, command: commands.Command) -> None:
        if not await command.can_run(self.context):
            return

        embed = self.get_command_embed(command)
        await self.send(embed)

    def get_group_embed(self, group: commands.Group) -> discord.Embed:
        embed = discord.Embed(
            title=group.qualified_name,
            description=group.description
        )

        for command in group.walk_commands():
            embed.add_field(
                name=f'`{self.get_command_signature(command)}`',
                value=command.description
            )

        return embed

    async def send_group_help(self, group: commands.Group) -> None:
        if not group.can_run(self.context):
            return

        embed = self.get_group_embed(group)
        await self.send(embed)

    def get_cog_embed(self, cog: commands.Cog) -> discord.Embed:
        embed = discord.Embed(
            title=cog.qualified_name,
            description=cog.description
        )

        for command in cog.walk_commands():
            embed.add_field(
                name=f'`{self.get_command_signature(command)}`',
                value=command.description
            )

        return embed

    async def send_cog_help(self, cog: commands.Cog) -> None:
        embed = self.get_cog_embed(cog)
        await self.send(embed)


class Help(commands.Cog):
    def __init__(self, bot: BookShelf):
        self.bot = bot

    async def cog_load(self) -> None:
        help_command = HelpCommand()
        help_command.cog = self
        help_command._command_impl.description = f'The help command for {self.bot.user.name}.'

        self.bot.help_command = help_command


async def setup(bot: BookShelf):
    await bot.add_cog(Help(bot))
