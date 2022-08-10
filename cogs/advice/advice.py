from __future__ import annotations

import random
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from .api import AdviceSlipClient

if TYPE_CHECKING:
    from bot import BookShelf


class Advice(AdviceSlipClient, commands.Cog):
    def __init__(self, bot: BookShelf):
        self.bot = bot
        super().__init__()

    @commands.hybrid_group(
        name='advice',
        description='Get some advice!'
    )
    async def hybrid_advice(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(ctx.command)

    @hybrid_advice.command(
        name='random',
        description='Random advice.'
    )
    async def hybrid_random(self, ctx: commands.Context):
        data = await self.random_advice()
        embed = discord.Embed(
            title=data['slip']['advice'],
            color=discord.Color.random()
        )
        await ctx.send(embed=embed)

    @hybrid_advice.command(
        name='search',
        description='Search some advice.'
    )
    async def hybrid_search(self, ctx: commands.Context, query: str):
        data = await self.search_advice(query)

        if 'message' in data:
            text = data['message']['text']
            await ctx.send(text)
            return

        slip = random.choice(data['slips'])
        embed = discord.Embed(
            title=slip['advice'],
            color=discord.Color.random()
        )
        await ctx.send(embed=embed)
