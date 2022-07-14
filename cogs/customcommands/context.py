from __future__ import annotations

import discord
from discord.ext import commands


class CustomCommandContext:
    def __init__(self, ctx: commands.Context):
        self.author = Author(ctx.author, True)
        self.channel = Channel(ctx.channel, True)
        self.guild = Guild(ctx.guild, True)
        self.server = self.guild
        self.message = ctx.message.content.lstrip(f'{ctx.message.content}{ctx.invoked_with}')


class Base:
    def __init__(self, context: bool = False):
        self.__context = context

    @property
    def _prefix(self) -> str:
        return 'ctx.' if self.__context else ''


class Author(Base):
    def __init__(self, member: discord.Member, context: bool = False, reference_name: str = 'author'):
        super().__init__(context)
        self.name = member.name
        self.discriminator = member.discriminator
        self.nick = member.display_name
        self.mention = member.mention
        self.id = member.id
        self.__rn = reference_name

    def __str__(self):
        return f'{self.name}#{self.discriminator}'

    def __repr__(self):
        return f'{self._prefix}{self.__rn}.name = {self.name}\n' \
               f'{self._prefix}{self.__rn}.discriminator = {self.discriminator}\n' \
               f'{self._prefix}{self.__rn}.nick = {self.nick}\n' \
               f'{self._prefix}{self.__rn}.mention = {self.mention}'


class Channel(Base):
    def __init__(self, channel: discord.abc.GuildChannel, context: bool = False):
        super().__init__(context)
        self.name = channel.name
        self.mention = channel.mention

    def __str__(self):
        return self.mention

    def __repr__(self):
        return f'{self._prefix}channel.name = {self.name}\n{self._prefix}channel.mention = {self.mention}'


class Guild(Base):
    def __init__(self, guild: discord.Guild, context: bool = False):
        super().__init__(context)
        self.name = guild.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self._prefix}guild.name = {self.name}'


class MiniContext:
    def __init__(self, ctx: commands.Context):
        self.guild = discord.Object(id=ctx.guild.id)
        self.author = str(ctx.author)

    def to_dict(self) -> dict:
        data = {
            'guild_id': str(self.guild.id),
            'author': self.author
        }
        return data

    @classmethod
    def from_dict(cls, data: dict) -> MiniContext:
        self = cls.__new__(cls)
        self.guild = discord.Object(int(data['guild_id']))
        self.author = data['author']
        return self
