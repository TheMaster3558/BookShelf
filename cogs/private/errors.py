from __future__ import annotations

import io
import sys
import traceback
from typing import TYPE_CHECKING, Type

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from bot import BookShelf


class ErrorHandler(commands.Cog):
    secret_perms: tuple[Type[commands.CheckFailure], ...] = (
        commands.MissingPermissions,
        app_commands.MissingPermissions,
        commands.NotOwner,
    )

    def __init__(self, bot: BookShelf):
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help(ctx.command)

        elif isinstance(error, self.secret_perms):
            await ctx.send('You don\'t have permissions to run this command.', ephemeral=True)

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(str(error), ephemeral=True)

        elif isinstance(error, commands.TooManyArguments):
            return

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(f'`{ctx.command.qualified_name} cannot be used in DMs.`', ephemeral=True)

        elif isinstance(error, commands.RangeError):
            await ctx.send(f'"{ctx.current_parameter.name}" must be `{error.minimum}-{error.maximum}`'
                           f', not `{error.value}`.', ephemeral=True)

        elif isinstance(error, commands.BadArgument):
            await self.bad_argument_handler(ctx, error)

        else:
            if await self.bot.is_owner(ctx.author):
                temp = io.StringIO()

                traceback.print_exception(
                    type(error),
                    error,
                    error.__traceback__,
                    file=temp
                )
                tb = temp.getvalue()

                try:
                    await ctx.send(f'```py\n{tb}\n```')
                except discord.HTTPException:
                    await ctx.send('Something went wrong. Check the console for more.')
                    traceback.print_exception(
                        type(error),
                        error,
                        error.__traceback__,
                        file=sys.stderr
                    )

            else:
                traceback.print_exception(
                    type(error),
                    error,
                    error.__traceback__,
                    file=sys.stderr
                )

    async def bad_argument_handler(self, ctx: commands.Context, error: commands.BadArgument) -> None:
        if isinstance(error, (commands.MemberNotFound, commands.UserNotFound)):
            await ctx.send('That user was not found.', ephemeral=True)
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send(f'I couldn\'t convert that to a channel.', ephemeral=True)
        elif isinstance(error, commands.GuildNotFound):
            await ctx.send('That server was not found.', ephemeral=True)
        else:
            await ctx.send(str(error))


async def setup(bot: BookShelf) -> None:
    await bot.add_cog(ErrorHandler(bot))
