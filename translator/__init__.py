import asyncio
import re

import argostranslate.package, argostranslate.translate
import discord
from discord import app_commands


MISSING = discord.utils.MISSING


class Translator(app_commands.Translator):
    validation_regex = re.compile(r'[-_\p{L}\p{N}\p{sc=Deva}\p{sc=Thai}]{1,32}')

    def __init__(self):
        self.translators: dict[str, argostranslate.translate.ITranslation] = {}

    def install_languages(self):
        codes = [e.value.split('-')[0] for e in discord.Locale]

        argostranslate.package.update_package_index()
        available_packages = [
            package for package in argostranslate.package.get_available_packages()
            if package.from_code == 'en' and package.to_code in codes
        ]

        for package in available_packages:
            package.install()

        languages = argostranslate.translate.get_installed_languages()

        english: argostranslate.translate.Language = MISSING
        for language in languages:
            if language.code == 'en':
                english = language

        assert english is not MISSING

        for language in languages:
            translator = english.get_translation(language)
            self.translators[language.code] = translator

    async def translate(
            self,
            string: app_commands.locale_str,
            locale: discord.Locale,
            context: app_commands.TranslationContext
    ) -> str | None:
        if not self.translators:
            await asyncio.to_thread(self.install_languages)

        locale = locale.value.split('-')[0]  # type: ignore
        try:
            translations = self.translators[locale].hypotheses(str(string))
        except KeyError:
            return None
