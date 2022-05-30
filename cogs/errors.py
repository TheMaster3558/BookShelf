from typing import TYPE_CHECKING, Type, Optional

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from bot import BookShelf


class ErrorHandler(commands.Cog):
    secret_perms: tuple[Type[commands.CheckFailure]] = (
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
        else:
            raise error