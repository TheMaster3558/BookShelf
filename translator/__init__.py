import json

import aiofiles
import discord
from discord import app_commands


MISSING = discord.utils.MISSING


class Translator(app_commands.Translator):
    def __init__(self):
        self.translator = ...
        self.cache = {}

    async def load_cache(self):
        async with aiofiles.open('./translator/cache.json', 'r') as file:
            raw = await file.read()

        try:
            self.cache = json.loads(raw)
        except json.JSONDecodeError:
            async with aiofiles.open('./translator/cache.json', 'w') as file:
                await file.write('{}')
            await self.load_cache()

    async def save_cache(self):
        dumped = json.dumps(self.cache)

        async with aiofiles.open('./translator/cache.json', 'w') as file:
            await file.write(dumped)

    async def load(self) -> None:
        await self.load_cache()

    async def unload(self) -> None:
        await self.translator.close()
        await self.save_cache()

    async def translate(
            self,
            string: app_commands.locale_str,
            locale: discord.Locale,
            context: app_commands.TranslationContext
    ) -> str | None:
        translated = self.cache.get(
            f'{string}_{locale.value}',  # type: ignore
            string
        )
        return self.cache.setdefault(f'{string}_{locale.value}', translated)  # type: ignore

