from .foass import FOASS


async def setup(bot):
    await bot.add_cog(FOASS(bot))
