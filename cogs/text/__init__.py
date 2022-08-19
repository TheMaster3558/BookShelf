from .text import Text


async def setup(bot) -> None:
    await bot.add_cog(Text(bot))
