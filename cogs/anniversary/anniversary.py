from __future__ import annotations

import asyncio
import datetime
import math
import random
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands, tasks

import checks
from .database import AnniversaryDatabase

if TYPE_CHECKING:
    from bot import BookShelf


class Anniversary(AnniversaryDatabase, commands.Cog):
    number_to_word: dict[int, str] = {
        1: 'first',
        2: 'second',
        3: 'third',
        4: 'fourth',
        5: 'fifth',
        6: 'sixth',
        7: 'seventh',
        8: 'eighth',
        9: 'ninth',
        10: 'tenth'
    }

    discord_blurple_changed = datetime.datetime(
        2021,
        3,
        13,
        tzinfo=datetime.timezone.utc
    )

    def __init__(self, bot: BookShelf):
        self.bot = bot
        super().__init__()

    async def cog_load(self):
        await super().cog_load()
        self.check_years.start()

    async def cog_unload(self):
        self.check_years.cancel()
        await super().cog_unload()

    @tasks.loop(hours=6)
    async def check_years(self):
        users = {k: v for k, v in await self.get_all_users()}
        now = discord.utils.utcnow()

        for user in self.bot.users:
            created_at = user.created_at

            if now >= datetime.datetime(
                now.year,
                created_at.month,
                created_at.day,
                created_at.hour,
                created_at.minute,
                created_at.second,
                created_at.microsecond,
                tzinfo=created_at.tzinfo
            ) and users.get(user.id, 0) != now.year and (now - created_at).days >= 365:
                year = math.ceil((now - user.created_at).days / 365)
                embed = self.make_embed(user, year)
                try:
                    await user.send(embed=embed)
                except (discord.HTTPException, AttributeError):
                    pass
                await self.add_year(user, now.year)

                await asyncio.sleep(0.2)

    @check_years.before_loop
    async def wait_until_ready(self):
        await self.bot.wait_until_ready()

    def get_embed_color(self, user: discord.User) -> discord.Color:
        if user.created_at >= self.discord_blurple_changed:
            blurple = discord.Color.blurple()
        else:
            blurple = discord.Color.og_blurple()
        return random.choice((blurple, discord.Color.magenta()))

    def make_embed(self, user: discord.User, year: int) -> discord.Embed:
        embed = discord.Embed(
            title=f'It\'s your {self.number_to_word[year]} anniversary of joining Discord! 🥳🎂',
            description='Have a great rest of your day!',
            color=self.get_embed_color(user)
        )
        return embed

    @commands.hybrid_command(
        name='anniversary',
        description='When your next anniversary of joined discord is.'
    )
    @app_commands.describe(user='The user to get the next anniversary.')
    async def hybrid_anniversary(self, ctx: commands.Context, user: discord.User = commands.Author):
        now = discord.utils.utcnow()
        next_anniversary = user.created_at

        while next_anniversary < now:
            next_anniversary = datetime.datetime(
                next_anniversary.year + 1,
                next_anniversary.month,
                next_anniversary.day,
                next_anniversary.hour,
                next_anniversary.minute,
                next_anniversary.second,
                next_anniversary.microsecond,
                tzinfo=next_anniversary.tzinfo
            )

        age = math.ceil((next_anniversary - user.created_at).days / 365)

        embed = discord.Embed(
            title=f'{discord.utils.format_dt(next_anniversary, style="R")}, {user} will reach '
                  f'their {self.number_to_word[age]} anniversary.',
            color=self.get_embed_color(user)
        )
        await ctx.send(embed=embed)
