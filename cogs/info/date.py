import datetime

import discord
from discord.ext import commands


class DateConverter(commands.Converter):
    current_year = discord.utils.utcnow().year
    offset_timedelta = datetime.timedelta(days=1)

    async def convert(self, ctx: commands.Context, argument: str) -> datetime.datetime:
        year: int | str

        try:
            day, month = argument.split('/')

            if '/' in month:
                month, year = argument.split('/')
            else:
                year = self.current_year

            if isinstance(year, str) and len(year) < 4:
                while len(year) < 3:
                    year = '0' + year
                year = '2' + year

            return datetime.datetime(int(year), int(month), int(day)) + self.offset_timedelta
        except ValueError as e:
            raise commands.BadArgument('Expected date in format `<day>/<month>/[year]`')


date_parameter = commands.parameter(converter=DateConverter, default=None, displayed_default='<any>')
