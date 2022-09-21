from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from utils import InteractionCreator, VirtualContext
from .database import RolesDatabase
from .views import EmbedBuilderModal, RoleOptionView, RoleView, RoleEditView

if TYPE_CHECKING:
    from bot import BookShelf


class Roles(RolesDatabase, commands.Cog, description='Do some cool stuff with roles in your server.'):
    """Do some cool stuff with roles in your server."""
    def __init__(self, bot: BookShelf):
        self.bot = bot
        self.active_message_ids: list[int] = []
        super().__init__()

    @commands.hybrid_group(
        name='role',
        description='Role related commands.'
    )
    async def hybrid_role(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @hybrid_role.command(
        name='select',
        description='Allow users to get roles with a select menu.'
    )
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def app_select(self, ctx: commands.Context, channel: discord.TextChannel):
        modal = EmbedBuilderModal()

        if ctx.interaction:
            interaction = ctx.interaction
        else:
            view = InteractionCreator(ctx.author, timeout=None)
            await ctx.send(view=view)
            await view.wait()
            interaction = view.interaction

        await interaction.response.send_modal(modal)
        await modal.wait()

        embed = discord.Embed(
            title=modal.title_.value
        )
        embed.set_image(url=modal.image.value)
        embed.set_footer(text=modal.footer.value)

        if not embed:
            await modal.interaction.response.send_message(
                'You need to enter at least one value.',
                ephemeral=True
            )

        view = RoleOptionView()
        await modal.interaction.response.send_message(view=view, embed=view.embed)
        view.message = await modal.interaction.original_response()
        await view.wait()

        if not view.options:
            return

        roles = [option.value for option in view.options]
        descriptions = [option.description for option in view.options]
        emojis = [option.emoji for option in view.options]
        author = interaction.user

        view = RoleView(view.options)

        try:
            message = await channel.send(embed=embed, view=view)
        except discord.HTTPException:
            await interaction.followup.send(
                f'I couldn\'t send a message in {channel.mention}.',
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title='Note',
            description=f'If a role is deleted or something similar, use the `role edit` command.'
        )
        await interaction.followup.send(
            embed=embed
        )

        self.active_message_ids.append(message.id)
        self.messages.append(message.id)
        await self.insert(roles, descriptions, emojis, author, message)

    @hybrid_role.command(
        name='edit',
        description='Edit a role select menu.'
    )
    async def hybrid_edit(self, ctx: commands.Context, message: discord.Message):
        if message.id not in self.messages:
            await ctx.send('That message is not a role select menu.', ephemeral=True)
            return
        if ctx.author.id != await self.get_author(message):
            await ctx.send('You can\'t edit this!')
            return

        embed = message.embeds[0]
        options = message.components[0].children[0].options
        view = RoleEditView(options)
        await ctx.send(embed=embed, view=view)
        await view.wait()

        embed = view.embed
        options = view.select.options

        roles = [option.value for option in options]
        descriptions = [option.description for option in options]
        emojis = [option.emoji for option in options]

        await self.delete(message)
        await self.insert(roles, descriptions, emojis, ctx.author, message, updating=True)

        view = RoleView(options)
        await message.edit(embed=embed, view=view)

    # listeners
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.message or interaction.message.id not in self.messages:
            return

        await interaction.response.defer()

        if interaction.message.id in self.active_message_ids:
            return

        options: list[discord.SelectOption] = []
        for role_id, description, emoji in await self.get_roles(interaction.message):
            role = interaction.guild.get_role(int(role_id))

            if emoji == 'None':
                emoji = None
            else:
                ctx = VirtualContext(guild=interaction.guild, bot=interaction.client)
                try:
                    emoji = await commands.EmojiConverter().convert(ctx, emoji)  # type: ignore
                except commands.EmojiConverter:
                    pass

            option = discord.SelectOption(
                label=role.name,
                emoji=emoji,
                description=description,
                value=str(role.id)
            )
            options.append(option)

        view = RoleView(options)
        self.bot.add_view(view, message_id=interaction.message.id)
        self.active_message_ids.append(interaction.message.id)

        await view.children[0].callback(interaction)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.id in self.messages:
            await self.delete(message)

