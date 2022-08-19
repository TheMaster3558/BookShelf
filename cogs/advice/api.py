from __future__ import annotations

import json
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from bot import BookShelf


class AdviceSlipClient:
    bot: BookShelf

    BASE: ClassVar[str] = 'https://api.adviceslip.com/advice'

    async def random_advice(self) -> dict:
        async with self.bot.session.get(self.BASE) as resp:
            text = await resp.text()  # for some reason resp.json() doesn't work
            return json.loads(text)

    async def search_advice(self, query: str) -> dict:
        async with self.bot.session.get(f'{self.BASE}/search/{query}') as resp:
            text = await resp.text()
            return json.loads(text)

