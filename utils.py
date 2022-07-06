from __future__ import annotations

from math import ceil
from typing import Any, Optional, overload, TypeVar

import discord
import numpy

MISSING = discord.utils.MISSING


class InteractionCreator(discord.ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interaction: discord.Interaction = MISSING

    @discord.ui.button(label='Click to start!', style=discord.ButtonStyle.green)
    async def creator(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.interaction = interaction
        self.stop()


class AuthoredView(discord.ui.View):
    def __init__(self, author: discord.abc.Snowflake | None, *, timeout: Optional[float] = 180):
        self.author = author
        super().__init__(timeout=timeout)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not self.author:
            return True
        if interaction.user == self.author:
            return True
        await interaction.response.send_message('This is not for you', ephemeral=True)
        return False


class VirtualContext:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    async def send(self, *args, **kwargs) -> discord.Message | None:
        if hasattr(self, 'channel'):
            return await self.channel.send(*args, **kwargs)

    async def typing(self, *args, **kwargs) -> None:
        pass


async def split_embeds(embeds: list[discord.Embed], channel: discord.abc.Messageable) -> None:
    embeds_list = [list(array) for array in numpy.array_split(embeds, ceil(len(embeds) / 10))]  # type: ignore

    for embeds in embeds_list:
        await channel.send(embeds=embeds)


class AlmostInteractionContext:
    def __init__(self, interaction: discord.Interaction):
        self.bot = interaction.client
        self.guild = interaction.guild


KT = TypeVar('KT')
VT = TypeVar('VT')


@overload
def get_max(population: dict[KT, VT], greater_than: None = None) -> KT:
    ...


@overload
def get_max(population: dict[KT, VT], greater_than: Any) -> Optional[KT]:
    ...


def get_max(population: dict[KT, VT], greater_than: Optional[Any] = None) -> Optional[KT]:
    highest = max(population, key=population.get)  # type: ignore
    if not greater_than or population[highest] > greater_than:
        return highest
