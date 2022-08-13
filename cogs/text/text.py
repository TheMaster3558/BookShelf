from __future__ import annotations

from typing import TYPE_CHECKING

import discord
import owoify
from discord import app_commands
from discord.ext import commands

from .views import ReplaceView, UwufiyView

if TYPE_CHECKING:
    from bot import BookShelf


class Text(commands.GroupCog):
    def __init__(self, bot: BookShelf):
        self.bot = bot

    @commands.hybrid_command(
        name='uwuify',
        descritpion='uwu.'
    )
    @app_commands.describe(text='The text to uwuify.')
    async def hybrid_uwuify(self, ctx: commands.Context, *, text: str):
        view = UwufiyView(ctx.author)
        msg = await ctx.send(view=view)
        await view.wait()

        text = owoify.owoify(text, view.select.level)
        await msg.edit(content=text, view=None)

    @commands.hybrid_command(
        name='replace',
        description='Replace a character with another.'
    )
    async def hybrid_replace(self, ctx: commands.Context, *, text: str):
        embed = discord.Embed(
            title='Here are your replacements',
            description=''
        )
        view = ReplaceView(embed, ctx.author)
        await ctx.send(embed=embed, view=view)
        await view.wait()

        text = text.translate(view.replacements)
        await ctx.send(text)

