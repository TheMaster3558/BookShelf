import asyncio
import datetime
from io import BytesIO
from typing import Any, Generator

import discord
from colorgram import extract  # type: ignore

from .database import EmbedStorage


def get_perms_name(perms: discord.Permissions) -> Generator[str, Any, Any]:
    return (perm.capitalize().replace('_', ' ') for perm, value in perms if value)


class EmbedBuilder(EmbedStorage):
    def build_user_embed(self, user: discord.User | discord.Member, date: datetime.datetime | None
                         ) -> discord.Embed:
        maybe = self.get(user, date)
        if maybe:
            return maybe

        embed = discord.Embed(
            title=str(user),
            description=user.mention,
            color=user.color,
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(
            url=user.display_avatar.url
        )
        embed.set_footer(
            text=f'ID: {user.id}'
        )
        embed.add_field(
            name='Joined Discord',
            value=discord.utils.format_dt(user.created_at)
        )

        if isinstance(user, discord.User):
            self.insert(user.id, embed, 'user')

        return embed

    def build_member_embed(self, member: discord.Member, date: datetime.datetime | None) -> discord.Embed:
        assert member.joined_at is not None

        maybe = self.get(member, date)
        if maybe:
            return maybe

        embed = self.build_user_embed(member, date)
        embed.add_field(
            name='Joined Server',
            value=discord.utils.format_dt(member.joined_at)
        )
        embed.add_field(
            name='Roles',
            value=' '.join(role.mention for role in member.roles),
            inline=False
        )
        embed.add_field(
            name='Server Permissions',
            value=', '.join(get_perms_name(member.guild_permissions))
        )

        self.insert(member.id, embed, 'member')

        return embed

    async def build_guild_embed(self, guild: discord.Guild, date: datetime.datetime | None) -> discord.Embed:
        maybe = self.get(guild, date)
        if maybe:
            return maybe

        embed = discord.Embed(
            title=guild.name,
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(
            text=f'Guild ID: {guild.id}'
        )

        if (icon := guild.icon) is not None:
            embed.set_thumbnail(url=icon.url)
            file = BytesIO()
            await icon.save(file)

            colors = await asyncio.to_thread(extract, file, 1)
            r, g, b = colors[0].rgb
            embed.color = discord.Color.from_rgb(r, g, b)  # type: ignore # property has setter

        embed.add_field(
            name='Created',
            value=discord.utils.format_dt(guild.created_at)
        )
        embed.add_field(
            name='Text Channels',
            value=len(guild.text_channels)
        )
        embed.add_field(
            name='Category Channels',
            value=len(guild.categories)
        )
        embed.add_field(
            name='Voice Channels',
            value=len(guild.voice_channels)
        )
        embed.add_field(
            name='System Channel',
            value=guild.system_channel.mention if guild.system_channel else None
        )
        embed.add_field(
            name='Members',
            value=guild.member_count
        )
        embed.add_field(
            name='Roles',
            value=' '.join(role.mention for role in reversed(guild.roles))
        )

        self.insert(guild.id, embed, 'guild')

        return embed

    def build_role_embed(self, role: discord.Role, date: datetime.datetime | None) -> discord.Embed:
        maybe = self.get(role, date)
        if maybe:
            return maybe

        embed = discord.Embed(
            title=role.name,
            description=role.mention,
            color=role.color,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(
            name='Created At',
            value=discord.utils.format_dt(role.created_at)
        )
        embed.add_field(
            name='Bot Role',
            value=role.is_bot_managed()
        )
        embed.add_field(
            name='Nitro Role',
            value=role.is_premium_subscriber()
        )
        embed.add_field(
            name='Member Count',
            value=len(role.mention)
        )
        embed.add_field(
            name='Hierarchy Position',
            value=role.position
        )
        embed.add_field(
            name='Permissions',
            value=', '.join(get_perms_name(role.permissions)),
            inline=False
        )

        if role.icon:
            icon = role.icon.url
        else:
            icon = None

        embed.set_footer(text=f'Role ID: {role.id}', icon_url=icon)

        self.insert(role.id, embed, 'role')

        return embed

