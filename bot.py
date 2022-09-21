import asyncio
import logging
from typing import Any, Callable, Coroutine, Optional, TypeVar

import aiohttp
import discord
from discord.ext import commands


T = TypeVar('T')


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
        'cogs.foaas',
        'cogs.private',
        'jishaku',
        'cogs.timestamps',
        'cogs.secretinvites',
        'cogs.text',
        'cogs.roles',
        'cogs.logs'
    ]

    test_guild = discord.Object(id=878431847162466354)

    def __init__(self, nasa_api_key: Optional[str] = None):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__('bk ', intents=intents)

        self.session: aiohttp.ClientSession = MISSING

        self.nasa_api_key = nasa_api_key
        if self.nasa_api_key:
            self.initial_extensions.append('cogs.nasa')
        if self.intents.members:
            self.initial_extensions.append('cogs.anniversary')

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

    # extra utils

    @staticmethod
    async def get_or_fetch(async_method: Callable[[int], Coroutine[Any, Any, T]], snowflake: int) -> T:
        sync_method_name: str = async_method.__name__.replace('fetch', 'get')
        sync_method: Callable[[int], T] = getattr(
            async_method.__self__, sync_method_name   # type: ignore
        )

        return sync_method(snowflake) or await async_method(snowflake)
