from __future__ import annotations

from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from utils import AuthoredView


MISSING = discord.utils.MISSING


class WritingModal(discord.ui.Modal, title='Write a story'):
    name: discord.ui.TextInput = discord.ui.TextInput(
        label='Name',
        placeholder='The name of the story'
    )

    text: discord.ui.TextInput = discord.ui.TextInput(
        label='Text',
        placeholder='Your story here',
        style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

    def get_values(self) -> tuple[str, str]:
        name = self.name.value or ''
        text = self.text.value or ''
        return name, text


class WriteSelect(discord.ui.Select['AuthoredView']):
    def __init__(self, writes: list[tuple[str, str]]):
        self.writes = dict(writes)

        options = [
            discord.SelectOption(label=name) for name, _ in self.writes.items()
        ]
        super().__init__(
            options=options,
            placeholder='Select a story',
            min_values=1,
            max_values=1
        )

        self.value: tuple[str, str] = MISSING

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        self.disabled = True
        await interaction.edit_original_message(view=self.view)

        self.value = (self.values[0], self.writes[self.values[0]])
        self.view.stop()  # type: ignore


class AuthorSelect(discord.ui.Select['AuthoredView']):
    def __init__(self, names: list[str]):
        options = [
            discord.SelectOption(label=name) for name in names
        ]
        super().__init__(
            options=options,
            placeholder='Select an author',
            min_values=1,
            max_values=1
        )

        self.author: str = MISSING

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        self.disabled = True
        await interaction.edit_original_message(view=self.view)

        self.author = self.values[0]
        self.view.stop()  # type: ignore
