from __future__ import annotations

import zlib
from typing import TYPE_CHECKING

import aiofiles
from discord.ext import commands, tasks

if TYPE_CHECKING:
    from bot import BookShelf


class Backup(commands.Cog):
    databases = (
        './cogs/customcommands/command_storage.json',
        './cogs/democracy/democracy.db',
        './cogs/info/embed_storage.json',
        './cogs/nasa/channels.db',
        './cogs/share/share.db'
    )

    URL = 'https://actualdarlingscientificcomputing.chawkk.repl.co'

    def __init__(self, bot: BookShelf):
        self.bot = bot

    @tasks.loop(minutes=20)
    async def backup_task(self):
        await self.backup()

    @backup_task.after_loop
    async def finish(self):
        await self.backup()

    # actually fetching the backup data will be made if we ever need it

    async def backup(self):
        data = await self.get_data()

        for kwargs in data:
            async with self.bot.session.post(f'{self.URL}/backup', **kwargs) as resp:
                if not resp.ok:
                    break

    async def get_data(self) -> list[dict[str, str | bytes]]:
        backup_data = []

        for filename in self.databases:
            async with aiofiles.open(filename, 'rb') as file:
                binary = await file.read()

            kwargs = {
                'params': {
                    'filename': filename,
                    'bytes': 'true' if filename.endswith('.db') else 'false'
                },
                'data': zlib.compress(binary)
            }
            backup_data.append(kwargs)

        return backup_data


async def setup(bot: BookShelf):
    await bot.add_cog(Backup(bot))
