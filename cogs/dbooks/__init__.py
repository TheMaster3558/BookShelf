from .dbooks import DBooks


async def setup(bot) -> None:
    await bot.add_cog(DBooks(bot))
