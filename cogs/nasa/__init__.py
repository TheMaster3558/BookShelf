from .nasa import NASA


async def setup(bot):
    await bot.add_cog(NASA(bot))
