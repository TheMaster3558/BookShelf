from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import discord
from discord.ext import commands

from .views import FOASSView

if TYPE_CHECKING:
    from bot import BookShelf


def call_with_author(ctx: commands.Context, func: Callable[..., str], *args) -> str:
    return func(*args, ctx.author)


class FOASS(commands.Cog):
    def __init__(self, bot: BookShelf):
        self.bot = bot
        super().__init__()

    @commands.hybrid_command(
        name='foass',
        description='Say some colorful things to your friends!'
    )
    async def hybrid_foass(self, ctx: commands.Context):
        view = FOASSView(ctx.author)
        await ctx.send(view=view, ephemeral=True)
        await view.wait()

        message = call_with_author(ctx, view.method, *view.args)
        await ctx.send(message)
