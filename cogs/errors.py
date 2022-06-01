from __future__ import annotations

import sys
import traceback
from typing import TYPE_CHECKING, Type

from discord.ext import commands

if TYPE_CHECKING:
    from bot import BookShelf


class ErrorHandler(commands.Cog):
    secret_perms: tuple[Type[commands.CheckFailure], ...] = (
        commands.MissingPermissions,
        commands.NotOwner
    )

    def __init__(self, bot: BookShelf):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help(ctx.command)
        elif isinstance(error, self.secret_perms):
            return
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(f'`{ctx.command.qualified_name} cannot be used in DMs.`')
        elif isinstance(error, commands.RangeError):
            await ctx.send(f'"{ctx.current_parameter.name}" must be `{error.minimum}-{error.maximum}`'
                           f', not `{error.value}`.')
        else:
            traceback.print_exception(
                type(error),
                error,
                error.__traceback__,
                file=sys.stderr
            )


async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
