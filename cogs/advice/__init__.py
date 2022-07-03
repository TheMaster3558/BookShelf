from .advice import Advice


async def setup(bot):
    await bot.add_cog(Advice(bot))
