from io import StringIO
from typing import TypeAlias

import asteval  # type: ignore
from discord.ext import commands


class CodeblockConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str):
        argument = argument.strip('`')

        if argument.startswith('py'):
            argument = argument[2:]

        return argument


code_block_converter = commands.parameter(converter=CodeblockConverter, displayed_default='<code_block>')


StdOut: TypeAlias = 'StringIO'
StdErr: TypeAlias = 'StringIO'


class AstevalEval:
    def __init__(self):
        self.interpreters: dict[int, asteval.Interpreter] = {}

    def get_interpreter(self, user_id: int) -> asteval.Interpreter:
        if user_id not in self.interpreters:
            stdout, stderr = StringIO(), StringIO()

            self.interpreters[user_id] = asteval.Interpreter(
                writer=stdout, err_writer=stderr
            )
        return self.interpreters[user_id]

    @staticmethod
    def format_err(err: str) -> str:
        return f'\u001b[0;31m{err}'

    def run_eval(self, code: str, user_id: int):
        interpreter = self.get_interpreter(user_id)

        interpreter.eval(code)

        msg = interpreter.writer.getvalue()

        if error := interpreter.err_writer.getvalue():
            msg += f'\n\n{self.format_err(error)}'

        # make new string io's to reset outputs
        interpreter.writer, interpreter.err_writer = StringIO(), StringIO()

        return f'```ansi\n{msg}\n```' if msg.replace(' ', '') else f'No output'
