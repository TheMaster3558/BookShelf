from __future__ import annotations

import aiofiles
import json
from typing import TYPE_CHECKING, MutableSequence

import discord
from discord.ext import commands

from .arguments import Argument
from .context import CustomCommandContext, MiniContext

if TYPE_CHECKING:
    from bot import BookShelf


MISSING = discord.utils.MISSING


async def run_converters(ctx: commands.Context, args: list[Argument], new_args: list) -> list:
    limited_ctx = CustomCommandContext(ctx)

    for index, arg in enumerate(args):
        if len(new_args) <= index:
            if arg.default is None:
                raise ValueError()

            default = arg.default

            if default.startswith('ctx.'):
                default = getattr(limited_ctx, default[4:], 'None')

            new_args.append(default)

            continue

        if arg.annotation is not None:
            new_args[index] = await arg.annotation().convert(ctx, new_args[index])
    return new_args


class CommandStorage:
    bot: BookShelf

    def __init__(self):
        self.commands_to_store: list[Command] = []

    def create_command(
            self, *, name: str, args: list[Argument], output: str, ctx: commands.Context | MiniContext
    ) -> Command:
        @commands.command(
            name=name,
            description=f'Created by {ctx.author}',
            cls=Command
        )
        @commands.check(lambda cctx: cctx.guild.id == ctx.guild.id)
        async def custom_command(cctx: commands.Context, *new_args):
            if len(new_args) < len([arg for arg in args if arg.default is not None]):  # type: ignore
                await cctx.send_help(cctx.command)
                return

            mutable_args = list(new_args)
            converted_args = await run_converters(cctx, args.copy(), mutable_args)

            format_kwargs = {arg.name: converted_args[index] for index, arg in enumerate(args)}
            to_send = output.format(**format_kwargs)
            await cctx.send(to_send)

        custom_command.output = output
        custom_command.ctx = MiniContext(ctx)
        custom_command.args = args

        self.commands_to_store.append(custom_command)

        return custom_command

    async def to_file(self):
        data = [command.to_dict() for command in self.commands_to_store]

        async with aiofiles.open('./cogs/customcommands/command_storage.json', 'w') as file:
            dumped = json.dumps(data, indent=4)
            await file.write(dumped)

    async def from_file(self):
        async with aiofiles.open('./cogs/customcommands/command_storage.json', 'r') as file:
            raw = await file.read()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            async with aiofiles.open('./cogs/customcommands/command_storage.json', 'w') as file:
                await file.write('{}')
            return await self.from_file()

        command_data: dict
        for command_data in data:
            name = command_data['name']
            args = [Argument.from_dict(arg) for arg in command_data['args']]
            output = command_data['output']
            ctx = MiniContext.from_dict(command_data['ctx'])

            command = self.create_command(
                name=name, args=args, output=output, ctx=ctx
            )
            self.bot.add_command(command)

    async def cog_load(self):
        await self.from_file()

    async def cog_unload(self):
        await self.to_file()


class Command(commands.Command):
    def __init__(self, func, **kwargs):
        super().__init__(func, **kwargs)
        self.output: str = MISSING
        self.ctx: MiniContext = MISSING
        self.args: list[Argument] = MISSING

    def to_dict(self) -> dict:
        data = {
            'name': self.name,
            'ctx': self.ctx.to_dict(),
            'output': self.output,
            'args': [
                arg.to_dict() for arg in self.args
            ]
        }
        return data

    async def error_handler(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, ValueError):
                await ctx.send('The `output` for this command may have not been formatted correctly.'
                               'Try deleting and remaking it.')
                return
        if isinstance(error, commands.CheckFailure):
            return

        raise error
