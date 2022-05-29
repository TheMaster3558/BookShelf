import logging

import aiohttp
import discord
from discord.ext import commands


MISSING = discord.utils.MISSING


def setup_logging():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='logs/discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    logger = logging.getLogger('asyncio')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='logs/asyncio.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


def cythonize():
    import os
    from Cython.Build import cythonize

    for file in os.listdir('./cython/'):
        if file.endswith('.pyx'):
            cythonize(file)


class BookShelf(commands.Bot):
    __version__ = '1.0.0a'

    initial_extensions = (
        'cogs.share',
        'cogs.dbooks',
        'cogs.democracy',
        'cogs.python'
    )
    test_guild = discord.Object(id=878431847162466354)

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__('bk ', intents=intents)

        self.session: aiohttp.ClientSession = MISSING

        setup_logging()

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
        await self.tree.sync()
