from __future__ import annotations

import datetime
import random
from typing import TYPE_CHECKING, Literal, Optional

import discord
from discord import app_commands
from discord.ext import commands, tasks

from .api import NASAClient
from .database import Database
from .views import ExplanationView

import checks
from utils import VirtualContext

if TYPE_CHECKING:
    from bot import BookShelf


class RandomFlags(commands.FlagConverter, delimiter=' ', prefix='--'):
    random: Optional[bool] = None

    def __bool__(self):
        return self.random is not None


class DateConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str):
        try:
            years, months, days = argument.split('-')
        except ValueError:
            raise commands.BadArgument('`date` must be in format `YYYY-MM-DD`.')
        return f'{years}-{months}-{days}'


class NASA(Database, NASAClient, commands.Cog):
    get_date = lambda *args, **kwargs: discord.utils.utcnow()

    def __init__(self, bot: BookShelf):
        self.bot = bot
        self.first_start = True
        self.dates_done: list[str] = []
        super().__init__()

    async def cog_load(self):
        await super().cog_load()
        self.first_start = True
        self.autopost_apod.start()

    async def cog_unload(self):
        self.first_start = False
        self.autopost_apod.cancel()
        await super().cog_unload()

    @tasks.loop(minutes=20)
    async def autopost_apod(self):
        date = self.get_date().strftime('%Y-%m-%d')
        if not await self.apod(date):
            if not self.first_start:
                return

            date = (self.get_date() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            if not await self.apod(date):
                return

        if date in self.dates_done:
            return
        self.dates_done.append(date)

        for channel_tuple in await self.get_channels():
            channel_id = channel_tuple[0]
            try:
                channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
            except discord.HTTPException:
                continue

            ctx = VirtualContext(channel=channel, author=None)
            await self.hybrid_apod.callback(self, ctx, date)

    @autopost_apod.before_loop
    async def wait_until_ready(self):
        await self.bot.wait_until_ready()

    @commands.hybrid_group(
        name='apodchannel',
        description='Autopost the APOD in a channel.'
    )
    @checks.hybrid_has_permissions(administrator=True)
    async def hybrid_apodchannel(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @hybrid_apodchannel.command(
        name='set',
        description='Set the channel.'
    )
    @app_commands.describe(
        channel='The channel to set.'
    )
    @commands.has_permissions(administrator=True)
    async def hybrid_set(self, ctx: commands.Context, channel: discord.TextChannel):
        await self.add_channel(channel)
        await ctx.send(f'Channel set to {channel.mention}.')

    @hybrid_apodchannel.command(
        name='remove',
        description='Remove the channel.'
    )
    @commands.has_permissions(administrator=True)
    async def hybrid_remove(self, ctx: commands.Context):
        await self.delete_channel(ctx.guild)
        await ctx.send('There is not longer an APOD autopost channel.')

    @commands.hybrid_command(
        name='apod',
        description='NASA astronomy picture of the day!',
        extras={
            'flags': {
                '--random': 'Whether to pick a random date. Cannot be combined with a date.'
            }
        }
    )
    @app_commands.describe(
        date='The date in YYYY-MM-DD format.',
        random='Whether to randomly choose the date.'
    )
    async def hybrid_apod(self, ctx: commands.Context | VirtualContext,
                          date: Optional[DateConverter] = None,
                          *, flags: RandomFlags = None):
        if ctx:
            await ctx.typing()

        if not flags or not flags.random:
            if not date:
                date = self.get_date().strftime('%Y-%m-%d')
            data = await self.apod(date)
        else:
            data = await self.apod(count=1)
            data = data[0]

        embed = discord.Embed(
            title=data['title'],
            url=data['url'],
            timestamp=datetime.datetime.strptime(data['date'], '%Y-%m-%d')
        )
        embed.set_footer(
            text=f'Copyright: {data.get("copyright", "None")}'
        )
        if 'thumbnail_url' in data:
            embed.set_image(url=data['thumbnail_url'])
        elif 'hdurl' in data:
            embed.set_image(url=data['hdurl'])

        view = ExplanationView(data['explanation'], ctx.author)

        await ctx.send(embed=embed, view=view)

    @commands.hybrid_command(
        name='mars',
        description='Get pictures of mars rovers!'
    )
    @app_commands.describe(
        rover='The rover to get images from.'
    )
    async def hybrid_mars(self, ctx: commands.Context,
                          rover: Literal['curiosity', 'opportunity', 'spirit'] = None):
        rover = rover or random.choice(('curiosity', 'opportunity', 'spirit'))
        data = await self.mars(rover)
        data = random.choice(data['photos'])

        embed = discord.Embed(
            title=f'{data["rover"]["name"]} {data["camera"]["full_name"]}'
        )
        embed.set_image(url=data['img_src'])
        await ctx.send(embed=embed)
