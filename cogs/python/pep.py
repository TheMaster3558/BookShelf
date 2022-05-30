from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

import discord

if TYPE_CHECKING:
    from bot import BookShelf


MISSING = discord.utils.MISSING


class PEPs:
    bot: BookShelf

    URL: ClassVar[str] = 'https://peps.python.org/api/peps.json'
    peps: dict[str, dict]

    async def cog_load(self):
        async with self.bot.session.get(self.URL) as resp:
            self.__class__.peps = await resp.json()

    def get_pep(self, pep: str) -> discord.Embed:
        if pep not in self.peps:
            embed = discord.Embed(
                title=f'PEP {pep} was not found.'
            )
        else:
            data = self.peps[pep]
            title = data['title']
            authors = data['authors']
            type_of_pep = data['type']
            created_at = data['created'].replace('-', ' ')
            python_version = data['python_version'] or 'None'
            replaces = data['replaces']
            replaced_by = data['superseded_by']
            url = data['url']

            embed = discord.Embed(
                title=f'PEP {pep} - {title}',
                url=url
            )
            embed.add_field(
                name='Author(s)',
                value=authors
            )
            embed.add_field(
                name='Type',
                value=type_of_pep
            )
            embed.add_field(
                name='Created At',
                value=created_at
            )
            embed.add_field(
                name='Python Version',
                value=python_version
            )
            embed.add_field(
                name='Replaces',
                value=replaces
            )
            embed.add_field(
                name='Replaced By',
                value=replaced_by
            )

        return embed






