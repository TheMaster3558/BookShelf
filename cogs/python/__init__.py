from .python import Python


async def setup(bot) -> None:
    await bot.add_cog(Python(bot))
