from .anniversary import Anniversary


async def setup(bot) -> None:
    await bot.add_cog(Anniversary(bot))
