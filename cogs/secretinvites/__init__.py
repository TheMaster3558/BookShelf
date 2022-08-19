from .secretinvites import SecretInvites


async def setup(bot) -> None:
    await bot.add_cog(SecretInvites(bot))
