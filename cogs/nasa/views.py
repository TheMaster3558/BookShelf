import discord

from utils import AuthoredView


class ExplanationView(AuthoredView):
    def __init__(self, explanation: str, author: discord.abc.Snowflake | None):
        self.explanation = explanation
        super().__init__(author, timeout=None)

    @discord.ui.button(label='Explanation')
    async def description_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_message(self.explanation, ephemeral=True)
