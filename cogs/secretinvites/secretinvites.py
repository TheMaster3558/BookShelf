from __future__ import annotations

import asyncio
import datetime
import random
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

import checks
from utils import async_yielder

if TYPE_CHECKING:
    from bot import BookShelf


class SecretInvites(commands.Cog):
    def __init__(self, bot: BookShelf):
        self.bot = bot
        self.cached_invites: dict[int, list[discord.Invite]] = {}
        self.guild_invites_ready: dict[int, asyncio.Event] = {}
        super().__init__()

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        self.cached_invites[guild.id] = []
        self.guild_invites_ready[guild.id] = asyncio.Event()
        await asyncio.sleep(120)

        if not guild.me.guild_permissions.manage_channels:
            return
        try:
            invites = await guild.invites()
        except discord.Forbidden:
            pass
        else:
            self.cached_invites[guild.id].extend(invites)
        finally:
            self.guild_invites_ready[guild.id].set()

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        if not invite.guild:
            return

        if invite.guild.id in self.guild_invites_ready:
            await self.guild_invites_ready[invite.guild.id].wait()

        self.cached_invites[invite.guild.id].append(invite)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        if not invite.guild:
            return

        if invite.guild.id in self.guild_invites_ready:
            await self.guild_invites_ready[invite.guild.id].wait()

        try:
            self.cached_invites[invite.guild.id].remove(invite)
        except ValueError:
            pass

    async def populate_cache(self):
        await self.bot.wait_until_ready()
        self.cached_invites = {guild.id: [] for guild in self.bot.guilds}
        self.guild_invites_ready = {guild.id: asyncio.Event() for guild in self.bot.guilds}

        async for guilds in async_yielder(self.bot.guilds, count=10, delay=10):
            for guild in guilds:
                if not guild.me.guild_permissions.manage_channels:
                    continue
                try:
                    invites = await guild.invites()
                except discord.Forbidden:
                    pass
                else:
                    self.cached_invites[guild.id].extend(invites)
                finally:
                    self.guild_invites_ready[guild.id].set()

    async def cog_load(self) -> None:
        await super().cog_load()
        self.bot.loop.create_task(self.populate_cache())

    @commands.hybrid_command(
        name='secretinvite',
        description='Get a secret invite without anyone knowing!'
    )
    @app_commands.describe(
        guild='The ID of the server to use, defaults to current server.'
    )
    @checks.hybrid_has_permissions(create_instant_invite=True)
    async def hybrid_get(self, ctx: commands.Context, guild: discord.Guild = commands.CurrentGuild):
        if not self.cached_invites.get(guild.id, []):
            await ctx.send('No cached invites for this server, try again later.', ephemeral=True)
            return

        invites = self.cached_invites[guild.id]
        invite = random.choice(invites)

        expires_at = discord.utils.format_dt(
            invite.created_at + datetime.timedelta(seconds=invite.max_age),
            style='R'
        ) if invite.max_age != 0 else 'Never'

        embed = discord.Embed(
            title='Invite Found',
            url=invite.url
        )
        embed.add_field(
            name='Creator',
            value=str(invite.inviter)
        )
        embed.add_field(
            name='Max Uses',
            value=str(invite.max_uses) if invite.max_uses != 0 else 'Unlimited'
        )
        embed.add_field(
            name='Expires At',
            value=expires_at
        )
        embed.add_field(
            name='Code',
            value=invite.code
        )
        embed.add_field(
            name='Link',
            value=invite.url
        )
        embed.add_field(
            name='Channel',
            value=invite.channel.mention
        )
        embed.set_footer(text=f'Guild: {invite.guild.name}')
        await ctx.send(embed=embed, ephemeral=True)
