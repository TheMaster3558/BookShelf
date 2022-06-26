from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from .embed import EmbedBuilder

if TYPE_CHECKING:
    from bot import BookShelf


class Info(EmbedBuilder, commands.Cog):
    """Get info about roles, members, etc."""
    def __init__(self, bot: BookShelf):
        self.bot = bot

    @commands.hybrid_command(
        name='userinfo',
        description='Get info about a member or user.'
    )
    @app_commands.describe(
        user='The user to get info from'
    )
    async def hybrid_userinfo(self, ctx: commands.Context,
                              user: discord.Member | discord.User = commands.Author):
        if isinstance(user, discord.Member):
            embed = self.build_member_embed(user)
        else:
            embed = self.build_user_embed(user)

        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name='serverinfo',
        description='Get info about a server.',
        aliases=['guildinfo']
    )
    @commands.guild_only()
    async def hybrid_serverinfo(self, ctx: commands.Context):
        embed = await self.build_guild_embed(ctx.guild)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name='roleinfo',
        description='Get info about a role.'
    )
    @app_commands.describe(
        role='The role to get info from'
    )
    async def hybrid_roleinfo(self, ctx: commands.Context, role: discord.Role):
        embed = self.build_role_embed(role)
        await ctx.send(embed=embed)
