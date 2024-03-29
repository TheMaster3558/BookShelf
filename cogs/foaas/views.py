from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Callable

import discord
from discord.ext import commands
import foaap

from utils import AuthoredView, AlmostInteractionContext

if TYPE_CHECKING:
    from .foaas import MiniArgs


MISSING = discord.utils.MISSING


class FOAASSelect(discord.ui.Select['FOAASView']):
    def __init__(self, options: list[str]):
        options = [
            discord.SelectOption(label=option.replace('_', ' ').capitalize(), value=option) for option in options
        ]
        super().__init__(placeholder='Select an option', options=options)

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.view.do_next(interaction, self)


class FOAASView(AuthoredView):
    SELECT_ONE = foaap.__all__[:25]
    SELECT_TWO = foaap.__all__[25:50]
    SELECT_THREE = foaap.__all__[50:75]
    SELECT_FOUR = foaap.__all__[75:]

    def __init__(self, author: discord.abc.Snowflake):
        super().__init__(author, timeout=None)
        self.method: Callable[..., str] = MISSING
        self.args: list[str] = []

        selects = (
            FOAASSelect(self.SELECT_ONE),
            FOAASSelect(self.SELECT_TWO),
            FOAASSelect(self.SELECT_THREE),
            FOAASSelect(self.SELECT_FOUR)
        )
        for select in selects:
            self.add_item(select)

    async def do_next(self, interaction: discord.Interaction, select: discord.ui.Select) -> None:
        self.method = getattr(foaap, select.values[0])

        if len(inspect.signature(self.method).parameters) <= 1:
            await interaction.response.defer()
        else:
            modal = FOAASModal(self.method, self)
            await interaction.response.send_modal(modal)
            await modal.wait()

        await interaction.message.delete()
        self.stop()


class FOAASModal(discord.ui.Modal):
    def __init__(self, method: Callable[..., str], view: FOAASView | MiniArgs):
        self.view = view

        self.method = method
        super().__init__(title='Enter the values')

        names: list[str] = list(method.__annotations__.keys())  # type: ignore

        try:
            del names[names.index('return')]
        except (IndexError, ValueError):
            pass

        try:
            del names[-1]
        except (IndexError, ValueError):
            pass

        for name in names:
            friendly_name = name.replace('_', ' ').capitalize()
            item = discord.ui.TextInput(label=friendly_name, custom_id=name)
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        text_input: discord.ui.TextInput
        for text_input in self.children:
            ctx = AlmostInteractionContext(interaction)

            try:
                user = await commands.MemberConverter().convert(ctx, text_input.value)  # type: ignore
            except commands.MemberNotFound:
                value = text_input.value
            else:
                value = user.mention

            self.view.args.append(value)
