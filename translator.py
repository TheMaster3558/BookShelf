import async_google_trans_new as google_trans

import discord
from discord import app_commands


MISSING = discord.utils.MISSING


class Translator(app_commands.Translator):
    def __init__(self):
        self.translator: google_trans.AsyncTranslator = MISSING

    async def load(self) -> None:
        self.translator = google_trans.AsyncTranslator(url_suffix='us')

    async def unload(self) -> None:
        await self.translator.close()

    async def translate(
            self,
            string: app_commands.locale_str,
            locale: discord.Locale,
            context: app_commands.TranslationContext
    ) -> str | None:
        return await self.translator.translate(string.message, locale.value)  # type: ignore


