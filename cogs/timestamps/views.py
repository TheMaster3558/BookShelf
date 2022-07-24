from datetime import datetime

import discord

from utils import InteractionCreator


MISSING = discord.utils.MISSING


months = (
    'January',
    'February',
    'March',
    'April',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
)


month_select = discord.ui.Select(
        placeholder='Month',
        options=[
            discord.SelectOption(label=m) for m in months
        ]
    )


month_text = discord.ui.TextInput(
    label='Month'
)


year = discord.ui.TextInput(
        label='Year'
    )


class TimestampModal(discord.ui.Modal, title='Timestamp Creator'):
    datetime_format = '%M %H %d %B %Y'

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

    @property
    def month(self) -> str:
        for child in self.children:
            if isinstance(child, discord.ui.Select) and child.placeholder == 'Month':
                return child.values[0]
            elif isinstance(child, discord.ui.TextInput) and child.label == 'Month':
                return child.value

    @property
    def year(self) -> discord.ui.TextInput:
        for child in self.children:
            if isinstance(child, discord.ui.TextInput) and child.label == 'Year':
                return child

    def __init__(self, author: discord.abc.Snowflake):
        super().__init__()
        self.author = author

        if isinstance(author, discord.Member) and not author.is_on_mobile():
            self.add_item(month_select)
        else:
            self.add_item(month_text)

        self.add_item(year)

        self.dt: datetime = MISSING
        self.style: str = MISSING

    async def on_submit(self, interaction: discord.Interaction) -> None:
        m_value = self.minutes.value
        h_value = self.hours.value
        d_value = self.days.value
        mo_value = self.month
        y_value = self.year.value

        while len(m_value) < 2:
            m_value = '0' + m_value
        while len(h_value) < 2:
            h_value = '0' + h_value
        while len(d_value) < 2:
            d_value = '0' + d_value
        while len(y_value) < 4:
            y_value = '0' + y_value

        format_text = f'{m_value} {h_value} {d_value} ' \
                      f'{mo_value} {y_value}'

        try:
            self.dt = datetime.strptime(format_text, self.datetime_format)
        except ValueError:
            await interaction.response.send_message('A part of the timestamp was invalid.', ephemeral=True)
            return

        if not isinstance(self.author, discord.Member) or not self.author.is_on_mobile():
            modal = StyleModal(self)
            view = InteractionCreator(interaction.user)
            await interaction.response.send_message('Now select a style!', view=view, ephemeral=True)
            await view.wait()
            await view.interaction.response.send_modal(modal)
            await modal.wait()
        else:
            self.style = None


class StyleModal(discord.ui.Modal, title='What style should it be?'):
    names = (
        'Short Time',
        'Short Date',
        'Long Date',
        'Short Date Time',
        'Long Date Time',
        'Relative Time'
    )

    styles = ('t', 'd', 'D', 'f', 'F', 'R')

    @property
    def style(self) -> discord.ui.Select:
        for child in self.children:
            if isinstance(child, discord.ui.Select) and child.placeholder == 'Select a style':
                return child

    def __init__(self, modal: TimestampModal):
        self.modal = modal
        super().__init__()

        dt = modal.dt
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

        style = discord.ui.Select(
            placeholder='Select a style',
            options=[
                discord.SelectOption(label=name, description=example, value=style)
                for name, example, style in zip(self.names, examples, self.styles)
            ]
        )
        self.add_item(style)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.modal.style = self.style.values[0]
        await interaction.response.send_message('Here you go!')
