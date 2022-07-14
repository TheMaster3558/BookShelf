from .anniversary import Anniversary


async def setup(bot):
    await bot.add_cog(Anniversary(bot))
