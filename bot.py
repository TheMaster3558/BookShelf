import asyncio
import logging
from typing import Optional

import aiohttp
import discord
from discord.ext import commands


MISSING = discord.utils.MISSING


def setup_logging(formatter: logging.Formatter):
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(formatter)
    discord_logger.addHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    discord_logger.addHandler(console_handler)

    asyncio_logger = logging.getLogger('asyncio')
    asyncio_logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='logs/asyncio.log', encoding='utf-8', mode='w')
    handler.setFormatter(formatter)
    asyncio_logger.addHandler(handler)


class BookShelf(commands.Bot):
    logging_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')

    initial_extensions = [
        'cogs.share',
        'cogs.dbooks',
        'cogs.democracy',
        'cogs.python',
        'cogs.info',
        'cogs.customcommands',
        'cogs.advice',
        'cogs.foass',
        'cogs.private'
    ]

    test_guild = discord.Object(id=878431847162466354)

    def __init__(self, nasa_api_key: Optional[str] = None):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__('bk ', intents=intents)

        self.session: aiohttp.ClientSession = MISSING

        self.nasa_api_key = nasa_api_key
        if self.nasa_api_key:
            self.initial_extensions.append('cogs.nasa')

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()

        for extension in self.initial_extensions:
            await self.load_extension(extension)

    async def close(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()
        await super().close()

    async def on_ready(self):
        print(f'Logged in as {self.user} | {self.user.id}')

    def standard_run(self, token: str, reconnect: bool = True, log: bool = True) -> None:
        async def runner():
            if log:
                setup_logging(self.logging_formatter)

            async with self:
                await self.start(token, reconnect=reconnect)

        asyncio.run(runner(), debug=True)
