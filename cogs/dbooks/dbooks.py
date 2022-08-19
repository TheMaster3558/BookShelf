from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from .api import DBooksClient

if TYPE_CHECKING:
    from bot import BookShelf


class DBooks(DBooksClient, commands.Cog):
    """Use the DBooks API (Which totally has all the books)."""
    def __init__(self, bot: BookShelf):
        self.bot = bot
        super().__init__()

    @commands.hybrid_command(
        name='searchbook',
        description='Search up a book on dbooks!'
    )
    @app_commands.describe(query='The book to search.')
    async def hybrid_search(self, ctx: commands.Context, query: str):
        await ctx.typing()
        data = await self.search(query)

        embed = discord.Embed(
            title=escape(data['title']),
            description=escape(data['subtitle']),
            url=data['url']
        )
        embed.add_field(
            name='Author(s)',
            value=data['authors']
        )

        read_url = data['url'] + 'read'

        embed.add_field(
            name='Read',
            value=read_url
        )

        embed.set_thumbnail(url=data['image'])

        await ctx.send(embed=embed)
