from .timestamps import Timestamps


async def setup(bot) -> None:
    await bot.add_cog(Timestamps(bot))
