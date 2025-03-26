# Copyright (C) 2025 Andrew Wason
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import enum
import readline  # for input()  # noqa: F401
import sqlite3
from collections.abc import Callable, Generator, AsyncIterator, Sequence
from typing import TYPE_CHECKING, Any
import itertools
import click

from rich.markdown import Markdown
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServer
from pydantic_ai.models import KnownModelName

from .render import console, render_text, render_markdown

class Command(enum.StrEnum):
    MULTI = "!multi"
    HELP = "!help"
    QUIT = "!quit"


async def chat(model: KnownModelName, markdown: bool, system_prompt: str | Sequence[str] = (), mcp_servers: Sequence[MCPServer] = ()) -> None:
    agent = Agent(model, system_prompt=system_prompt, mcp_servers=mcp_servers)

    console.print(f"[green]Chat - Ctrl-D or {Command.QUIT} to quit")
    console.print(f"[green]Enter {Command.MULTI} to enter/exit multiline mode, {Command.HELP} for more commands")

    async with agent.run_mcp_servers():
        message_history = None
        try:
            while True:
                prompt = input("> ")

                if prompt == Command.QUIT:
                    return
                elif prompt == Command.HELP:
                    console.print(f"[yellow]{Command.MULTI} - enter multiline mode, enter again to exit")
                    console.print(f"[yellow]{Command.HELP} - this message")
                    console.print(f"[yellow]{Command.QUIT} - quit (also Ctrl-D)")
                    continue
                elif prompt == Command.MULTI:
                    lines: list[str] = []
                    while (line := input(". ")) != Command.MULTI:
                        if line in Command:
                            console.print(
                                f"[red]Commands not accept in multiline mode, enter {Command.MULTI} to exit multiline"
                            )
                            continue
                        lines.append(line)
                    prompt = "\n".join(lines)

                try:
                    async with agent.run_stream(prompt, message_history=message_history) as result:
                        stream = result.stream_text(delta=True)
                        if markdown:
                            await render_markdown(stream)
                        else:
                            await render_text(stream)
                        message_history = result.all_messages() #XXX does not include final message due to delta?
                except Exception as e:
                    console.print(f"[red]Error: {str(e)[:2048]}")
        except EOFError:
            return
