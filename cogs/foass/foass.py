from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any, Callable, TypeVar, overload, Optional

import foaap
import discord
from discord import app_commands
from discord.ext import commands
from fuzzywuzzy import fuzz

from .views import FOASSView, FOASSModal

if TYPE_CHECKING:
    from bot import BookShelf

# Cython faster
try:
    from cython_bk.speed import get_max  # type: ignore
except ImportError:
    KT = TypeVar('KT')
    VT = TypeVar('VT')

    @overload
    def get_max(population: dict[KT, VT], greater_than: None) -> KT:
        ...

    @overload
    def get_max(population: dict[KT, VT], greater_than: Optional[Any]) -> Optional[KT]:
        ...

    def get_max(population: dict[KT, VT], greater_than: Optional[Any] = None) -> Optional[KT]:
        highest = max(population, key=population.get)  # type: ignore
        if not greater_than or population[highest] > greater_than:
            return highest


def call_with_author(ctx: commands.Context, func: Callable[..., str], *args) -> str:
    return func(*args, ctx.author)


class MiniArgs:
    def __init__(self):
        self.args = []


class FOASS(commands.Cog):
    def __init__(self, bot: BookShelf):
        self.bot = bot
        super().__init__()

    @commands.command(
        name='foass',
        description='Say some colorful things to your friends!'
    )
    async def message_foass(self, ctx: commands.Context):
        view = FOASSView(ctx.author)
        await ctx.send(view=view, ephemeral=True)
        await view.wait()

        message = call_with_author(ctx, view.method, *view.args)
        await ctx.send(message)

    @app_commands.command(
        name='foass',
        description='Say some colorful things to your friends!'
    )
    @app_commands.rename(
        _type='type'
    )
    @app_commands.guilds(878431847162466354)
    async def app_foass(self, interaction: discord.Interaction, _type: str):
        method = getattr(foaap, _type, None)
        if not method:
            await interaction.response.send_message(
                'That was not a valid type. Use the autocomplete.', ephemeral=True
            )
            return

        args = MiniArgs()
        modal = FOASSModal(method, args)
        await interaction.response.send_modal(modal)
        await modal.wait()

        ctx = await commands.Context.from_interaction(interaction)
        message = call_with_author(ctx, method, *args.args)
        await interaction.channel.send(message)

    @functools.cache
    @app_foass.autocomplete('_type')
    async def foass_type_autocomplete(self, interaction: discord.Interaction, current: str):
        current = current.lower()
        highest: dict[app_commands.Choice[str], int] = {}
        names: list[app_commands.Choice[str]] = []
        for name in foaap.__all__:
            name = name.lower()
            highest[app_commands.Choice(
                name=name.capitalize(), value=name
            )] = fuzz.token_sort_ratio(current, name)

        for _ in range(10):
            if len(current) >= 3:
                kwargs = {'greater_than': 50}
            else:
                kwargs = {}

            option = get_max(highest, **kwargs)
            if option:
                names.append(option)
                del highest[option]

        return names
