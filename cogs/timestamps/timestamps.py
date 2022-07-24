from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Literal

import discord
from discord import app_commands
from discord.ext import commands

from .views import TimestampModal
from utils import InteractionCreator

if TYPE_CHECKING:
    from bot import BookShelf


MISSING = discord.utils.MISSING


class Timestamps(commands.Cog):
    conversions = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 1,
        'December': 12
    }

    styles = {
        'Short Time': 't',
        'Long Time': 'T',
        'Short Date': 'd',
        'Long Date': 'D',
        'Short Date Time': 'f',
        'Long Date Time': 'F',
        'Relative Time': 'R'
    }

    def __init__(self, bot: BookShelf):
        self.bot = bot
        super().__init__()

    @commands.command(
        name='timestamp',
        description='Easily create a timestamp!'
    )
    async def message_timestamp(self, ctx: commands.Context):
        view = InteractionCreator(author=ctx.author)
        await ctx.send(view=view)
        await view.wait()

        await self.app_timestamp.callback(self, view.interaction, modal=True)

    @app_commands.command(
        name='timestamp',
        description='Easily create a timestamp!'
    )
    @app_commands.describe(
        second='The second in the timestamp.',
        minute='The minute in the timestamp.',
        hour='The hour in the timestamp. (24 hour time).',
        day='The day in the timestamp.',
        month='The month in the timestamp.',
        year='The year in the timestamp.',
        modal='Whether to send a modal. (Will not have seconds).'
    )
    async def app_timestamp(
            self,
            interaction: discord.Interaction,
            second: app_commands.Range[int, 0, 59] = None,
            minute: app_commands.Range[int, 0, 59] = None,
            hour: app_commands.Range[int, 1, 24] = None,
            day: app_commands.Range[int, 1, 31] = None,
            month: Literal['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December'] = None,
            year: app_commands.Range[int, 1970, 9999] = None,
            style: Literal['Short Time', 'Long Time', 'Short Date', 'Long Date',
                           'Short Date Time', 'Long Date Time', 'Relative Time'] = None,
            modal: bool = False,
    ):
        if modal:
            modal = TimestampModal(interaction.user)
            await interaction.response.send_modal(modal)
            await modal.wait()

            if modal.dt is MISSING:
                return

            try:
                dt = discord.utils.format_dt(modal.dt, style=modal.style)  # type: ignore
            except OSError:
                await interaction.followup.send('The date is too far in the past to convert to a timestamp.')
            else:
                await interaction.channel.send(f'{dt} `{dt}`')
            return

        if not all([second, minute, hour, day, month, year]):
            await interaction.response.send_message(
                'You must provide all time arguments if not using modals.',
                ephemeral=True
            )

        month = self.conversions[month]
        style = self.styles[style]
        dt_object = datetime(
            year, month, day, hour, minute, second
        )
        try:
            dt = discord.utils.format_dt(dt_object, style=style)
        except OSError:
            await interaction.followup.send('The date is too far in the past to convert to a timestamp.')
        else:
            await interaction.channel.send(f'{dt} `{dt}`')
