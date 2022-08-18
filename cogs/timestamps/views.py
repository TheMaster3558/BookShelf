from datetime import datetime

import discord


MISSING = discord.utils.MISSING


class TimestampModal(discord.ui.Modal, title='Timestamp Creator'):
    datetime_format = '%M %H %d %m %Y'

    minutes = discord.ui.TextInput(
        label='Minute',
        placeholder='0-59'
    )

    hours = discord.ui.TextInput(
        label='Hour',
        placeholder='1-24'
    )

    days = discord.ui.TextInput(
        label='Day',
        placeholder='1-31 (Depends on month)'
    )

    month = discord.ui.TextInput(
        label='Month',
        placeholder='1-12'
    )

    year = discord.ui.TextInput(
        label='Year',
        placeholder='1970+'
    )

    def __init__(self, author: discord.abc.Snowflake):
        super().__init__()
        self.author = author
        self.dt: datetime = MISSING
        self.interaction: discord.Interaction = MISSING

    async def on_submit(self, interaction: discord.Interaction) -> None:
        m_value = self.minutes.value
        h_value = self.hours.value
        d_value = self.days.value
        mo_value = self.month.value
        y_value = self.year.value

        while len(m_value) < 2:
            m_value = '0' + m_value
        while len(h_value) < 2:
            h_value = '0' + h_value
        while len(d_value) < 2:
            d_value = '0' + d_value
        while len(mo_value) < 2:
            mo_value = '0' + mo_value
        while len(y_value) < 4:
            y_value = '0' + y_value

        format_text = f'{m_value} {h_value} {d_value} ' \
                      f'{mo_value} {y_value}'

        try:
            self.dt = datetime.strptime(format_text, self.datetime_format)
        except ValueError as e:
            print(e)
            await interaction.response.send_message('A part of the timestamp was invalid.', ephemeral=True)
            return

        self.interaction = interaction
        self.stop()


class StyleSelect(discord.ui.Select['StyleView']):
    names = (
        'Short Time',
        'Short Date',
        'Long Date',
        'Short Date Time',
        'Long Date Time',
        'Relative Time'
    )

    styles = ('t', 'd', 'D', 'f', 'F', 'R')

    def __init__(self, dt: datetime):
        examples = [
            dt.strftime('%H:%M'),
            dt.strftime('%d/%m/%Y'),
            dt.strftime('%d %B %Y'),
            dt.strftime('%d %B %Y %H:%M'),
            dt.strftime('%A, %d %B %Y %H:%M')
        ]

        delta = dt - datetime.now()
        total_seconds = int(delta.total_seconds())

        if total_seconds in range(-60, 60):
            if total_seconds < 0:
                relative = f'{abs(total_seconds)} seconds ago'
            else:
                relative = f'in {total_seconds} seconds'
        elif total_seconds in range(-3600, 3600):
            if total_seconds < 0:
                relative = f'{abs(total_seconds // 60)} minutes ago'
            else:
                relative = f'in {total_seconds // 60} minutes'
        elif total_seconds in range(-86400, 86400):
            if total_seconds < 0:
                relative = f'{abs(total_seconds // 3600)} hours ago'
            else:
                relative = f'in {total_seconds // 3600} hours'
        elif total_seconds in range(-604800, 604800):
            if total_seconds < 0:
                relative = f'{abs(total_seconds // 86400)} days ago'
            else:
                relative = f'in {total_seconds // 86400} days'
        elif total_seconds in range(-2628000, 2628000):
            if total_seconds < 0:
                relative = f'{abs(total_seconds) // 604800} weeks ago'
            else:
                relative = f'in {total_seconds // 604800} weeks'
        elif total_seconds in range(-31536000, 31536000):
            if total_seconds < 0:
                relative = f'{abs(total_seconds) // 2628000} months ago'
            else:
                relative = f'in {total_seconds // 2628000} months'
        else:
            if total_seconds < 0:
                relative = f'{abs(total_seconds // 31536000)} years ago'
            else:
                relative = f'in {total_seconds // 31536000} years'

        examples.append(relative)

        options = [
            discord.SelectOption(label=name, description=example, value=style)
            for name, example, style in zip(self.names, examples, self.styles)
        ]

        super().__init__(
            options=options,
            placeholder='Select a style!'
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        self.disabled = True
        await interaction.message.edit(view=self.view)

        self.view.style = self.values[0]
        self.view.stop()


class StyleView(discord.ui.View):
    def __init__(self, dt: datetime):
        super().__init__(timeout=None)
        self.add_item(StyleSelect(dt))

        self.style: str = MISSING
