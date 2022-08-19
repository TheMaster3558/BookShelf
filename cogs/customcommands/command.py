from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from .arguments import Argument
    from .context import MiniContext


MISSING = discord.utils.MISSING


class CustomCommand(commands.Command):
    def __init__(self, func, **kwargs):
        super().__init__(func, **kwargs)
        self.output: str = MISSING
        self.ctx: MiniContext = MISSING
        self.args: list[Argument] = MISSING

    def to_dict(self) -> dict:
        data = {
            'name': self.name,
            'ctx': self.ctx.to_dict(),
            'output': self.output,
            'args': [
                arg.to_dict() for arg in self.args
            ]
        }
        return data

    async def error_handler(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandInvokeError) and isinstance(error.original, ValueError):
            await ctx.send('The `output` for this command may have not been formatted correctly.'
                           'Try deleting and remaking it.')
        elif isinstance(error, commands.CheckFailure):
            return
        else:
            raise error
