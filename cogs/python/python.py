from __future__ import annotations

import contextlib
import io
from typing import TYPE_CHECKING, ClassVar

import discord
from discord import app_commands
from discord.ext import commands

from .eval import AstevalEval, code_block_converter
from .views import CodeModal

if TYPE_CHECKING:
    from bot import BookShelf


class Python(AstevalEval, commands.Cog):
    zen: ClassVar[str] = ''

    def __init__(self, bot: BookShelf):
        self.bot = bot

        super().__init__()

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

