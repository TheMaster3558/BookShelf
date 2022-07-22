from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, Optional, overload

import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands

from utils import AuthoredView, InteractionCreator

from .database import ShareDatabase
from .views import AuthorSelect, WritingModal, WriteSelect
from utils import get_max

if TYPE_CHECKING:
    from bot import BookShelf


MISSING = discord.utils.MISSING


class Share(ShareDatabase, commands.Cog):
    """Share your writing with others!"""
    def __init__(self, bot: BookShelf):
        self.bot = bot
        self.read_count: dict[discord.User, int] = {}
        super().__init__()

    @commands.command(
        name='write',
        description='Write a story to share!'
    )
    async def message_write(self, ctx: commands.Context):
        creator = InteractionCreator(author=ctx.author, timeout=None)
        await ctx.send(view=creator)
        await creator.wait()

        await self.app_write.callback(self, creator.interaction)

    @app_commands.command(
        name='write',
        description='Write a story to share!'
    )
    async def app_write(self, interaction: discord.Interaction):
        modal = WritingModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        msg = await self.process_write(interaction.user, *modal.get_values())

        await interaction.followup.send(msg, ephemeral=True)

    @commands.hybrid_command(
        name='read',
        description='Read a story from a member!'
    )
    @app_commands.describe(
        author='The user to read stories from.'
    )
    async def hybrid_read(self, ctx: commands.Context, author: discord.User):
        try:
            writes = await self.fetch_writes(author)
        except aiosqlite.OperationalError:
            await ctx.send(f'{author} has not written anything.')
            return

        select = WriteSelect(writes)
        view = AuthoredView(ctx.author)
        view.add_item(select)

        await ctx.send(view=view)
        await view.wait()

        name, text = select.value

        ephemeral = False

        embeds = []
        embed = discord.Embed(title=name)
        embeds.append(embed)

        if len(text) > 4096:
            embed.description = text[:4095]

            embed2 = discord.Embed(description=text[4095:])
            embeds.append(embed2)
        else:
            embed.description = text

        if len(text) > 1000:
            ephemeral = True

        await ctx.send(embeds=embeds, ephemeral=ephemeral)

        if author not in self.read_count:
            self.read_count[author] = 0
        self.read_count[author] += 1

    @commands.hybrid_command(
        name='popular',
        description='Get some popular authors in this server!'
    )
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def hybrid_popular(self, ctx: commands.Context):
        copy = self.read_count.copy()

        popular = {k.name: v for k, v in copy.items()}
        popular_ids = {user.name: user.id for user in copy}
        popular_authors: list[str] = []

        for _ in range(5):
            try:
                author = get_max(popular)

                if not author:
                    break

                popular_authors.append(
                    author
                )
                del popular[author]
            except ValueError:
                break

        if len(popular_authors) < 1:
            await ctx.send('There are no popular authors in this server.', ephemeral=True)

        select = AuthorSelect(popular_authors)
        view = AuthoredView(ctx.author)
        view.add_item(select)

        await ctx.send(view=view)
        await view.wait()

        author_id = popular_ids[select.author]
        author = self.bot.get_user(author_id) or await self.bot.fetch_user(author_id)

        await self.hybrid_read.callback(self, ctx, author)
