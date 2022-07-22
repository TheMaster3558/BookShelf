from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Literal, TypeVar

if TYPE_CHECKING:
    from bot import BookShelf


KT = TypeVar('KT')
VT = TypeVar('VT')


class NASAClient:
    bot: BookShelf

    BASE: ClassVar[str] = 'https://api.nasa.gov'

    def cleanup_params(self, params: dict[KT, VT]) -> dict[KT, VT]:
        params = {k: v for k, v in params.items() if v is not None}
        params['api_key'] = self.bot.nasa_api_key
        return params

    async def apod(self, date: str | None = None, count: str | int = None, thumbs: bool = True) -> dict:
        params = self.cleanup_params({
            'date': date,
            'count': count,
            'thumbs': str(thumbs)
        })
        async with self.bot.session.get(f'{self.BASE}/planetary/apod', params=params) as resp:
            return await resp.json()

    async def mars(self, rover: Literal['curiosity', 'opportunity', 'spirit']) -> dict:
        params = self.cleanup_params({'sol': 1000})
        async with self.bot.session.get(f'{self.BASE}/mars-photos/api/v1/rovers/{rover}/photos',
                                        params=params) as resp:
            return await resp.json()
