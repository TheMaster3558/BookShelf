from .secretinvites import SecretInvites


async def setup(bot):
    await bot.add_cog(SecretInvites(bot))
