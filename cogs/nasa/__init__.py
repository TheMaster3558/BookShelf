from .nasa import NASA


async def setup(bot) -> None:
    await bot.add_cog(NASA(bot))
