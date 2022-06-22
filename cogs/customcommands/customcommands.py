from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from .arguments import Argument
from .context import Author, Channel, CustomCommandContext
from .database import CommandStorage

if TYPE_CHECKING:
    from bot import BookShelf


words_to_annotation: dict[str, type] = {
    'user': commands.MemberConverter,
    'channel': commands.GuildChannelConverter
}


class CustomCommands(CommandStorage, commands.Cog):
    def __init__(self, bot: BookShelf):
        self.bot = bot
        super().__init__()

    @commands.command(
        name='getclasses',
        description='Get the models for custom commands'
    )
    async def message_getclasses(self, ctx: commands.Context):
        new_ctx = CustomCommandContext(ctx)

        embed = discord.Embed(title='Context `ctx`')
        embed.add_field(
            name='Author',
            value=repr(new_ctx.author)
        )
        embed.add_field(
            name='Channel',
            value=repr(new_ctx.channel),
            inline=False
        )
        embed.add_field(
            name='Guild (server)',
            value=repr(new_ctx.guild),
            inline=False
        )
        embed.add_field(
            name='Message',
            value=f'ctx.message = {new_ctx.message or None}',
            inline=False
        )

        await ctx.send(embed=embed)

    async def ask_for_args(self, ctx: commands.Context, check) -> list[Argument] | None:
        args: list[Argument] = []

        await ctx.send('Type `stop` when you want to stop the arguments. Type `cancel` to cancel.')
        await asyncio.sleep(1)

        user = Author(ctx.author, reference_name='user')
        channel = Channel(ctx.channel)
        message = f'Type the name of an argument.\n`user` and `channel` are converted to models' \
                  f'\n{repr(user)}\n\n{repr(channel)}'
        await ctx.send(message)
        await asyncio.sleep(3)

        optional_yet: bool = False

        while True:
            await ctx.send('Send an argument now!')
            msg: discord.Message = await self.bot.wait_for('message', check=check)

            if msg.content == 'stop':
                break

            if msg.content == 'cancel':
                return None

            name = msg.content
            annotation = words_to_annotation.get(msg.content)

            await ctx.send(
                f'What do you want to default to be? Type `required` for a required argument. '
                f'You have access to `ctx` (`{ctx.clean_prefix}getclasses`).'
            )
            default_msg: discord.Message = await self.bot.wait_for('message', check=check)

            if default_msg.content == 'required':
                if optional_yet:
                    await ctx.send('You can\'t have a required argument after an optional argument.')
                    return None

                default = None
            elif default_msg.content == 'cancel':
                return None
            else:
                default = default_msg.content
                optional_yet = True

            argument = Argument(name, annotation, default)
            args.append(argument)

        return args

    async def ask_for_output(self, ctx: commands.Context, check) -> str:
        await ctx.send('Now send the output. You can use brackets `{}` to place arguments or use `ctx`. '
                       'For example, if the arguments were `user` and `number`, '
                       '`{user.name} drank {number} cups of water in {ctx.channel.name}`')
        message: discord.Message = await self.bot.wait_for('message', check=check)
        return message.content

    @commands.group(
        name='customcommands',
        description='Custom commands!',
        aliases=['customcommand', 'cc']
    )
    async def message_customcommands(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @message_customcommands.command(
        name='create',
        description='Create a custom command.'
    )
    async def message_create(self, ctx: commands.Context, name: str):
        check = lambda cctx: cctx.channel == ctx.channel and cctx.author == ctx.author

        args = await self.ask_for_args(ctx, check)

        if args is None:
            await ctx.send('Cancelled.')
            return

        output = await self.ask_for_output(ctx, check)

        command = self.create_command(
            name=name,
            args=args,
            output=output,
            ctx=ctx
        )
        self.bot.add_command(command)

        await ctx.send('Custom command successfully created.')

    @message_customcommands.command(
        name='delete',
        description='Delete a custom command.'
    )
    async def message_delete(self, ctx: commands.Context, name: str):
        for command in self.commands_to_store:
            if command.name == name and command.ctx.guild.id == ctx.guild.id:
                if ctx.author.guild_permissions.administrator or command.ctx.author == str(ctx.author):
                    self.commands_to_store.remove(command)
                    self.bot.remove_command(name)
                    await ctx.send('Command successfully deleted.')
                else:
                    await ctx.send('You can\'t delete this command.')
                return

        await ctx.send('That command was not found.')



