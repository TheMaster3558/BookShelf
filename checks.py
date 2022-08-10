from discord import app_commands
from discord.ext import commands


def hybrid_has_permissions(**perms):
    async def message_check(ctx: commands.Context):
        if ctx.interaction:
            return True
        return await commands.has_permissions(**perms).predicate(ctx)  # type: ignore

    def inner(command: commands.HybridCommand):
        command = app_commands.default_permissions(**perms)(command)
        return commands.check(message_check)(command)

    return inner

