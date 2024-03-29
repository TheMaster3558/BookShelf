from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from aiosqlite import OperationalError

import discord
from discord import app_commands
from discord.ext import commands, tasks

from .database import DemocracyDatabase
from utils import get_max, VirtualContext

if TYPE_CHECKING:
    from bot import BookShelf


class Democracy(DemocracyDatabase, commands.Cog):
    """A very simple implementation of democracy on discord."""
    def __init__(self, bot: BookShelf):
        self.bot = bot
        super().__init__()

    async def cog_load(self) -> None:
        await super().cog_load()
        self.check_elections.start()

    async def cog_unload(self) -> None:
        await super().cog_unload()
        self.check_elections.cancel()

    @tasks.loop(minutes=20)
    async def check_elections(self):
        elections = await self.get_end()

        for guild_id, time, channel_id in elections:
            time = datetime.fromisoformat(time)
            if time > discord.utils.utcnow():
                continue

            guild = await self.bot.get_or_fetch(self.bot.fetch_guild, guild_id)
            ctx: Any = VirtualContext(guild=guild)
            self.bot.loop.create_task(self.hybrid_finish(ctx))

    @check_elections.before_loop
    async def wait_until_ready(self):
        await self.bot.wait_until_ready()

    @commands.hybrid_group(
        name='election',
        description='Set up a democratic election!'
    )
    async def hybrid_election(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @hybrid_election.command(
        name='create',
        description='Create an election!'
    )
    @app_commands.describe(
        expiry='The days to end the election automatically in.',
        channel='The channel to send the election results in.'
    )
    @commands.has_permissions(administrator=True)
    async def hybrid_create(self, ctx: commands.Context,
                            expiry: int = commands.parameter(converter=commands.Range[int, 1, 7]),
                            channel: discord.TextChannel = commands.CurrentChannel):
        try:
            msg = await self.create_election(ctx.guild, expiry, channel)
        except OperationalError:
            await ctx.send('There is already a running election.')
            return
        
        await ctx.send(msg)

    @hybrid_election.command(
        name='vote',
        description='Vote for someone in an election!'
    )
    @app_commands.describe(
        member='The member to vote for.'
    )
    @commands.guild_only()
    async def hybrid_vote(self, ctx: commands.Context, member: discord.Member):
        try:
            updated = await self.user_vote(ctx.author, member)
        except OperationalError:
            await ctx.send('There is no election happening.', ephemeral=True)
            return

        if updated:
            text = f'Your vote has been updated to {member}.'
        else:
            text = f'You just voted for {member}.'

        await ctx.send(text, ephemeral=True)

    @hybrid_election.command(
        name='finish',
        description='Finish the election manually or early.'
    )
    @commands.has_permissions(administrator=True)
    async def hybrid_finish(self, ctx: commands.Context):
        try:
            channel_id = (await self.get_end(ctx.guild))[0][2]      
            data = await self.finish_election(ctx.guild)
        except (OperationalError, IndexError):
            await ctx.send('There is no election happening.', ephemeral=True)
            return

        candidates_id: dict[int, int] = {}

        for vote in data:
            vote_id = vote[0]
            candidates_id.setdefault(vote_id, 0)
            candidates_id[vote_id] += 1

        top: dict[int, int] = {}

        for _ in range(5):
            try:
                highest = get_max(candidates_id)

                if not highest:
                    break

                top[highest] = candidates_id[highest]
                del candidates_id[highest]
            except ValueError:
                break

        if len(top) < 1:
            await ctx.send('No one voted.')
            return

        top: dict[discord.Member, int] = {  # type: ignore
            await self.bot.get_or_fetch(ctx.guild.fetch_member, k): v
            for k, v in top.items()
        }

        embed = discord.Embed(
            title=f'{ctx.guild.name} Election Results',
            description=f'{list(top)[0].mention} has won the election!'  # type: ignore
        )

        for member, count in top.items():
            embed.add_field(name=str(member), value=f'{count} votes')

        channel = await self.bot.get_or_fetch(ctx.guild.fetch_channel, channel_id)

        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            await ctx.send(f'I don\'t have permission to send messages in {channel.mention}', ephemeral=True)
            await ctx.send(embed=embed)

