from .advice import Advice


async def setup(bot) -> None:
    await bot.add_cog(Advice(bot))
