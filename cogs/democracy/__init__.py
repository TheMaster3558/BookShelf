from .democracy import Democracy


async def setup(bot) -> None:
    await bot.add_cog(Democracy(bot))
