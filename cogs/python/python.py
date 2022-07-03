from __future__ import annotations

import contextlib
import io
from typing import TYPE_CHECKING, ClassVar, TypeVar

import discord
from discord import app_commands
from discord.ext import commands
from fuzzywuzzy import fuzz  # type: ignore

from .eval import AstevalEval, code_block_converter
from .pep import PEPs
from .views import CodeModal

# Cython faster
try:
    from cython.speed import get_max  # type: ignore
except ImportError:
    K = TypeVar('K')
    V = TypeVar('V')


    def get_max(population: dict[K, V]) -> K:
        return max(population, key=population.get)  # type: ignore

if TYPE_CHECKING:
    from bot import BookShelf


class Python(AstevalEval, PEPs, commands.Cog):
    """Eval, PEP's, and more!"""

    zen: ClassVar[str] = ''

    def __init__(self, bot: BookShelf):
        super().__init__()
        self.bot = bot

    @classmethod
    def get_zen(cls) -> str:
        if cls.zen:
            return cls.zen

        temp = io.StringIO()
        with contextlib.redirect_stdout(temp):
            import this

        cls.zen = temp.getvalue()
        return cls.get_zen()

    @commands.hybrid_command(
        name='zen',
        description='import this'
    )
    async def hybrid_zen(self, ctx: commands.Context):
        text = self.get_zen()
        new_text: list = text.split('\n')[2:]  # remove title
        text = '\n'.join(new_text)

        embed = discord.Embed(
            title='The Zen of Python (PEP 20) by Tim Peters',
            description=text,
            url='https://peps.python.org/pep-0020/'
        )
        await ctx.send(embed=embed)

    @commands.command(
        name='eval',
        description='Run some python code.'
    )
    async def message_eval(self, ctx: commands.Context, *, code: str = code_block_converter):
        out = self.run_eval(code, ctx.author.id)
        await ctx.send(out)

    @app_commands.command(
        name='eval',
        description='Run some python code.'
    )
    async def app_eval(self, interaction: discord.Interaction):
        modal = CodeModal()

        await interaction.response.send_modal(modal)
        await modal.wait()

        ctx = await commands.Context.from_interaction(interaction)
        await self.message_eval(ctx, code=modal.code.value)

    @commands.hybrid_command(
        name='pep',
        description='Python Enhancement Proposals.'
    )
    @app_commands.describe(
        pep='The PEP number'
    )
    async def hybrid_pep(self, ctx: commands.Context,
                         pep: str):
        embed = self.get_pep(pep)
        await ctx.send(embed=embed)

    @hybrid_pep.autocomplete('pep')
    async def pep_pep_autocomplete(self, interaction: discord.Interaction, current: str):
        current = current.lower()
        highest: dict[app_commands.Choice[str], int] = {}
        names: list[app_commands.Choice[str]] = []
        for name, key in self.all_names.items():
            name = name.lower()
            highest[app_commands.Choice(
                name=name.capitalize(), value=key
            )] = fuzz.token_sort_ratio(current, name)

        for _ in range(10):
            option = get_max(highest)
            names.append(option)
            del highest[option]

        return names
