from .foaas import FOAAS


async def setup(bot) -> None:
    await bot.add_cog(FOAAS(bot))
