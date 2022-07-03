import discord


class CodeModal(discord.ui.Modal, title='Eval'):
    code: discord.ui.TextInput = discord.ui.TextInput(
        label='Python Code',
        placeholder='print(\'Hello world\')',
        style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
