from .info import Info


async def setup(bot) -> None:
    await bot.add_cog(Info(bot))
