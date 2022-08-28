from __future__ import annotations

import asyncio

import discord
from discord.ext import commands

from utils import VirtualContext


MISSING = discord.utils.MISSING


class EmbedBuilderModal(discord.ui.Modal, title='Build an embed'):
    title_ = discord.ui.TextInput(
        label='Title',
        placeholder='Title of the embed',
        required=False
    )

    image = discord.ui.TextInput(
        label='Image',
        placeholder='Enter an image link',
        required=False
    )

    footer = discord.ui.TextInput(
        label='Footer',
        placeholder='Footer of the embed',
        required=False
    )

    def __init__(self):
        self.interaction: discord.Interaction = MISSING
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.interaction = interaction


class RoleOptionModal(discord.ui.Modal, title='Create a role option'):
    role = discord.ui.TextInput(
        label='Role',
        placeholder='ID or name'
    )

    emoji = discord.ui.TextInput(
        label='Emoji',
        placeholder='<name:id> or a literal emoji',
        required=False
    )

    description = discord.ui.TextInput(
        label='Description',
        placeholder='Enter the description for the select option here',
        required=False,
        max_length=32
    )

    def __init__(self, view: RoleOptionView):
        self.view = view
        super().__init__()

    def check_role(self, role: discord.Role) -> bool:
        return str(role.id) in [option.value for option in self.view.options]

    async def on_submit(self, interaction: discord.Interaction) -> None:
        ctx = VirtualContext(guild=interaction.guild, bot=interaction.client)

        try:
            role = await commands.RoleConverter().convert(ctx, self.role.value)  # type: ignore
        except commands.RoleNotFound:
            await interaction.response.send_message('That role was not found.', ephemeral=True)
            return

        if self.check_role(role):
            await interaction.response.send_message('You can\'t add duplicate roles.', ephemeral=True)
            return

        if self.emoji.value:
            try:
                emoji = await commands.EmojiConverter().convert(ctx, self.emoji.value)  # type: ignore
            except commands.EmojiNotFound:
                emoji = self.emoji.value
        else:
            emoji = None

        if self.description.value:
            description = self.description.value
        else:
            description = None

        option = discord.SelectOption(
            label=role.name,
            emoji=emoji,
            description=description,
            value=str(role.id)
        )
        self.view.options.append(option)

        self.view.embed.add_field(
            name=role.name,
            value=f'Emoji: {emoji} | Description: {description}',
            inline=False
        )
        await interaction.response.send_message('Role option added.', ephemeral=True)
        await self.view.message.edit(embed=self.view.embed)


class RoleOptionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.embed = discord.Embed(
            title='Current Roles'
        )
        self.options: list[discord.SelectOption] = []
        self.message: discord.Message = MISSING

    @discord.ui.button(label='Add Role', style=discord.ButtonStyle.green)
    async def add_role_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.options) >= 25:
            await interaction.response.send_message('The max is 25 roles.')
            return

        modal = RoleOptionModal(self)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label='Finish', style=discord.ButtonStyle.blurple)
    async def finish_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        self.add_role_button.disabled = True
        self.finish_button.disabled = True
        await interaction.message.edit(view=self)

        if not self.options:
            await interaction.response.send_message(
                'You must add at least one role.',
                ephemeral=True
            )
        self.stop()


class RoleSelect(discord.ui.Select['RoleView']):
    def __init__(self, options: list[discord.SelectOption]):
        super().__init__(
            options=options,
            min_values=0,
            max_values=len(options),
            placeholder='Select your roles!',
            custom_id=f'{type(self).__name__}'
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        selected = {interaction.guild.get_role(int(value)) for value in self.values}
        unselected = {
            interaction.guild.get_role(int(option.value))
            for option in self.options if option.value not in self.values
        }
        user_roles = set(interaction.user.roles)

        adding = selected - user_roles
        removing = unselected & user_roles

        await asyncio.sleep(0)

        try:
            if adding:
                await interaction.user.add_roles(
                    *adding,
                    reason=f'Select Menu Roles {interaction.message.id}'
                )
            if removing:
                await interaction.user.remove_roles(
                    *removing,
                    reason=f'Select Menu Roles {interaction.message.id}'
                )
        except discord.HTTPException:
            await interaction.followup.send(
                'Something went wrong adding/removing the roles.',
                ephemeral=True
            )
            raise

        message = ''
        if adding:
            message += f'Added {", ".join(role.name for role in adding)}.\n'
        if removing:
            message += f'Removed {", ".join(role.name for role in removing)}.'
        if not adding and not removing:
            message = 'No changes were made to your roles.'
        await interaction.followup.send(message, ephemeral=True)


class RoleView(discord.ui.View):
    def __init__(self, options: list[discord.SelectOption]):
        super().__init__(timeout=None)
        select = RoleSelect(options)
        self.add_item(select)


class RoleEditSelect(discord.ui.Select['RoleEditView']):
    def __init__(self, options: list[discord.SelectOption]):
        super().__init__(
            options=options,
            placeholder='Select an option to edit!'
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        self.view.edit_option_button.disabled = False
        self.view.delete_option_button.disabled = False

        option = None
        for option in self.options:
            if option.value == self.values[0]:
                self.view.selected_option = option
                break

        assert option is not None

        self.placeholder = f'Current editing option: {option.label}'
        await interaction.message.edit(view=self.view)


class RoleOptionEditModal(RoleOptionModal, title='Edit a role option'):
    view: RoleEditView

    async def on_submit(self, interaction: discord.Interaction) -> None:
        ctx = VirtualContext(guild=interaction.guild, bot=interaction.client)

        try:
            role = await commands.RoleConverter().convert(ctx, self.role.value)  # type: ignore
        except commands.RoleNotFound:
            await interaction.response.send_message('That role was not found.', ephemeral=True)
            return

        if self.check_role(role):
            await interaction.response.send_message('That role has already been added.', ephemeral=True)
            return

        if self.emoji.value:
            try:
                emoji = await commands.EmojiConverter().convert(ctx, self.emoji.value)  # type: ignore
            except commands.EmojiNotFound:
                emoji = self.emoji.value
        else:
            emoji = None

        if self.description.value:
            description = self.description.value
        else:
            description = None

        self.view.selected_option.label = role.name
        self.view.selected_option.value = str(role.id)
        self.view.selected_option.emoji = emoji
        self.view.selected_option.description = description
        await interaction.response.defer()


class RoleOptionEditAddModal(RoleOptionModal):
    view: RoleEditView

    async def on_submit(self, interaction: discord.Interaction) -> None:
        ctx = VirtualContext(guild=interaction.guild, bot=interaction.client)

        try:
            role = await commands.RoleConverter().convert(ctx, self.role.value)  # type: ignore
        except commands.RoleNotFound:
            await interaction.response.send_message('That role was not found.', ephemeral=True)
            return

        if self.check_role(role):
            await interaction.response.send_message('That role has already been added.', ephemeral=True)
            return

        if self.emoji.value:
            try:
                emoji = await commands.EmojiConverter().convert(ctx, self.emoji.value)  # type: ignore
            except commands.EmojiNotFound:
                emoji = self.emoji.value
        else:
            emoji = None

        if self.description.value:
            description = self.description.value
        else:
            description = None

        self.view.select.add_option(
            label=role.name,
            emoji=emoji,
            description=description,
            value=str(role.id)
        )

        await interaction.response.send_message('Role option added.', ephemeral=True)


class RoleEditView(discord.ui.View):
    def __init__(self, options: list[discord.SelectOption]):
        super().__init__(timeout=None)
        self.select = RoleEditSelect(options)
        self.add_item(self.select)
        self.embed: discord.Embed = MISSING

        self.selected_option: discord.SelectOption = MISSING

    @property
    def options(self) -> list[discord.SelectOption]:
        return self.select.options

    @discord.ui.button(label='Edit Embed')
    async def edit_embed_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.embed = interaction.message.embeds[0]

        modal = EmbedBuilderModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        await modal.interaction.response.defer()

        if modal.title_:
            self.embed.title = modal.title_.value
        if modal.image:
            self.embed.set_image(url=modal.image.value)
        if modal.footer:
            self.embed.set_footer(text=modal.footer.value)

        await interaction.message.edit(embed=self.embed)

    @discord.ui.button(label='Edit Option', disabled=True)
    async def edit_option_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        modal = RoleOptionEditModal(self)  # type: ignore
        await interaction.response.send_modal(modal)
        await modal.wait()

        self.select.placeholder = 'Select a role to edit!'
        await interaction.message.edit(view=self)

    @discord.ui.button(label='Add Option', row=1)
    async def add_option_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        modal = RoleOptionEditAddModal(self)  # type: ignore
        await interaction.response.send_modal(modal)
        await modal.wait()
        await interaction.message.edit(view=self)

    @discord.ui.button(label='Delete Option', disabled=True, row=1)
    async def delete_option_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if len(self.select.options) <= 1:
            await interaction.response.send_message(
                'You need to keep at least one role.',
                ephemeral=True
            )
            return

        await interaction.response.defer()
        self.select.options.remove(self.selected_option)
        self.select.placeholder = 'Select an option to edit!'
        await interaction.message.edit(view=self)

    @discord.ui.button(label='Finish', style=discord.ButtonStyle.green)
    async def finish_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()

        for child in self.children:
            child.disabled = True  # type: ignore
        await interaction.message.edit(view=self)
        self.stop()
