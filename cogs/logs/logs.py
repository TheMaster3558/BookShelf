from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import discord
from discord import app_commands
from discord.ext import commands

import checks
from utils import InteractionCreator

if TYPE_CHECKING:
    from bot import BookShelf


class MobileSupportFlags(commands.FlagConverter, delimiter=' ', prefix='--'):
    mobile: Optional[bool] = True

    def __bool__(self):
        return self.mobile is True

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str) -> MobileSupportFlags:
        self = await super().convert(ctx, argument)
        if '--one-image' not in argument:
            self.one_image = False
        return self  # type: ignore


class Logs(commands.Cog):
    def __init__(self, bot: BookShelf):
        self.bot = bot
        self.snipes: dict[discord.abc.GuildChannel, discord.Message] = {}

    # sniping
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.author.bot and message.guild:
            self.snipes[message.channel] = message

    @commands.hybrid_command(
        name='snipe',
        description='Get the most recently deleted message in this channel!',
        extras={
            'flags': {
                '--mobile': 'Whether to only show one image to support mobile.'
            }
        }
    )
    @app_commands.describe(
        mobile='Whether to only show one iamge to support mobile.'
    )
    async def hybrid_snipe(self, ctx: commands.Context, *, flags: MobileSupportFlags = None):
        try:
            message = self.snipes[ctx.channel]
        except KeyError:
            await ctx.send('No recently deleted messages in this channel.')
            return

        embeds = []
        embed = discord.Embed(
            url=message.jump_url,
            timestamp=message.created_at
        )
        embed.set_author(
            name=str(message.author),
            icon_url=message.author.display_avatar.url
        )
        embeds.append(embed)

        if message.content:
            embed.description = message.content
        if message.reference:
            reference = message.reference.cached_message or await ctx.channel.fetch_message(
                message.reference.message_id
            )
            embed.add_field(
                name='Replied To',
                value=f'[Click here to jump!]({reference.jump_url})'
            )

        for file in message.attachments:
            if embed.image:
                image_embed = discord.Embed(url=message.jump_url).set_image(url=file.url)
                embeds.append(image_embed)
            else:
                embed.set_image(url=file.url)
            if flags:
                break

        await ctx.send(embeds=embeds)

    @staticmethod
    def logging_enabled(guild: discord.Guild) -> bool:
        return not not discord.utils.get(guild.categories, name='Bookshelf-Logs')

    @commands.hybrid_group(
        name='logging',
        description='Add logging to your server!'
    )
    @commands.bot_has_permissions(manage_channels=True)
    @checks.hybrid_has_permissions(administrator=True)
    async def hybrid_logging(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            await ctx.send_help(ctx.command)

    @hybrid_logging.command(
        name='enable',
        description='Setup logging.'
    )
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def hybrid_enable(self, ctx: commands.Context):
        if self.logging_enabled(ctx.guild):
            await ctx.send('Logging is already enabled!', ephemeral=True)
            return

        embed = discord.Embed(
            description='This will create a category with 2 channels. Click below to continue!'
        )
        view = InteractionCreator(ctx.author, timeout=None)
        await ctx.send(embed=embed, view=view)
        await view.wait()
        await view.interaction.response.defer()

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite.from_pair(
                deny=discord.Permissions(view_channel=True),
                allow=discord.Permissions.none()
            ),
            ctx.me: discord.PermissionOverwrite.from_pair(
                deny=discord.Permissions.none(),
                allow=discord.Permissions(view_channel=True, send_messages=True, manage_channels=True)
            )
        }
        category = await ctx.guild.create_category(
            name='Bookshelf-Logs',
            overwrites=overwrites,
            reason=f'Logging enabled by {ctx.author}'
        )
        await category.create_text_channel(name='settings')
        await category.create_text_channel(name='logs')
        await ctx.send('Channels created! It is recommended to check permissions.', ephemeral=True)

    @hybrid_logging.command(
        name='disable',
        description='Disable logging.'
    )
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def hybrid_disable(self, ctx: commands.Context):
        if not self.logging_enabled(ctx.guild):
            await ctx.send('Logging is not enabled.', ephemeral=True)
            return

        category = discord.utils.get(ctx.guild.categories, name='Bookshelf-Logs')
        await category.delete(reason=f'Logging deleted by {ctx.author}')
        await ctx.send('Logging successfully deleted!', ephemeral=True)
