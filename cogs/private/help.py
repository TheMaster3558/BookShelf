from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Sequence

import discord
from discord.ext import commands
from requests.structures import CaseInsensitiveDict

from utils import split_embeds
from cogs.customcommands import CustomCommand  # type: ignore

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
                embed = await self.get_cog_embed(cog)

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
        if 'flags' in command.extras:
            flags = '\n'.join(f'`{name}`: {description}' for name, description in command.extras['flags'].items())
            embed.add_field(
                name='Flags',
                value=flags
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
        if not await group.can_run(self.context):
            return

        embed = self.get_group_embed(group)
        await self.send(embed)

    async def get_runnable_commands(self, cog: commands.Cog) -> list[commands.Command]:
        command_list: dict[commands.Command, bool] = {}

        async def check(command: commands.Command):
            if await command.can_run(self.context):
                canrun = True
            else:
                canrun = False
            command_list[command] = canrun

        for cmd in cog.walk_commands():
            await check(cmd)

        return [command for command in cog.walk_commands() if command_list[command] is True]

    async def get_cog_embed(self, cog: commands.Cog) -> discord.Embed:
        embed = discord.Embed(
            title=cog.qualified_name,
            description=cog.description
        )

        for command in await self.get_runnable_commands(cog):
            embed.add_field(
                name=f'`{self.get_command_signature(command)}`',
                value=command.description
            )

        return embed

    async def send_cog_help(self, cog: commands.Cog) -> None:
        embed = await self.get_cog_embed(cog)

        if not len(embed.fields):
            invoked_with = f'{self.context.prefix}{self.context.invoked_with}'
            string = self.context.message.content[len(invoked_with)+1:]
            await self.get_destination().send(self.command_not_found(string))
            return

        await self.send(embed)

    def get_command_signature(self, command: commands.Command) -> str:
        if not isinstance(command, CustomCommand):
            return super().get_command_signature(command)

        start = f'{self.context.clean_prefix}{command.qualified_name} '

        for arg in command.args:
            arg_text = arg.name

            if arg.default:
                arg_text += f'={arg.default}'
                arg_text = f'[{arg_text}]'
            else:
                arg_text = f'<{arg_text}>'
            arg_text += ' '
            start += arg_text

        return start.rstrip()


class Help(commands.Cog):
    def __init__(self, bot: BookShelf):
        self.bot = bot
        super().__init__()

    async def cog_load(self) -> None:
        help_command = HelpCommand()
        help_command.cog = self
        help_command._command_impl.explanation = f'The help command for {self.bot.user.name}.'

        self.bot.help_command = help_command

    @commands.command(
        name='category',
        description='Get help on a just a category!',
        aliases=['cog']
    )
    async def message_category(self, ctx: commands.Context, category: str):
        cog = CaseInsensitiveDict(self.bot.cogs).get(category)

        if not cog:
            embed = discord.Embed(
                title='Category Not Found',
                description=f'{", ".join(self.bot.cogs)} are the categories.'
            )
            embed.set_footer(text='Some categories may not have commands.')
            await ctx.send(embed=embed)

        await ctx.send_help(cog)


async def setup(bot: BookShelf):
    await bot.add_cog(Help(bot))
