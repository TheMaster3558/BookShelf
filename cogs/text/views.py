import discord
from owoify.owoify import Owoness
from utils import AuthoredView


class UwuifySelect(discord.ui.Select['UwuifyView']):
    def __init__(self):
        options = [
            discord.SelectOption(label='owo', value='0', description='Low'),
            discord.SelectOption(label='uwu', value='1', description='Medium'),
            discord.SelectOption(label='uvu', value='2', description='High')
        ]
        super().__init__(
            placeholder='Select an level',
            options=options
        )

        self.level: int = -1

    def set_level(self):
        raw = self.values[0]

        match raw:
            case '0':
                self.level = Owoness.Owo
            case '1':
                self.level = Owoness.Uwu
            case '2':
                self.level = Owoness.Uvu

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.disabled = True
        self.set_level()

        await interaction.message.edit(view=self.view)
        self.view.stop()


class UwufiyView(AuthoredView):
    def __init__(self, author: discord.abc.Snowflake):
        super().__init__(timeout=None, author=author)
        self.select = UwuifySelect()
        self.add_item(self.select)


class ReplaceModal(discord.ui.Modal, title='What to replace sir?'):
    old = discord.ui.TextInput(label='Old')
    new = discord.ui.TextInput(label='New')

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()


class ReplaceView(AuthoredView):
    def __init__(self, embed: discord.Embed, author: discord.abc.Snowflake):
        super().__init__(timeout=None, author=author)
        self.replacements: dict[str, str] = {}
        self.embed = embed

    @discord.ui.button(label='Click to add', style=discord.ButtonStyle.green)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ReplaceModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.replacements[modal.old.value] = modal.new.value

        self.embed.description += f'\n{modal.old.value}->{modal.new.value}'
        await interaction.message.edit(embed=self.embed)

    @discord.ui.button(label='Finish', style=discord.ButtonStyle.blurple)
    async def finish_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.stop()


