# Copyright (C) 2025 Andrew Wason
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import enum
import readline  # for input()  # noqa: F401
from collections.abc import Sequence

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServer
from pydantic_ai.messages import FunctionToolCallEvent, ModelMessage
from pydantic_ai.models import KnownModelName

from .render import console, render

# type Renderer = Callable(response: AsyncIterator[str]) -> CoroutineType[Any, Any, str]


class Command(enum.StrEnum):
    MULTI = "!multi"
    HELP = "!help"
    QUIT = "!quit"


async def chat(
    model: KnownModelName,
    markdown: bool,
    system_prompt: str | Sequence[str] = (),
    mcp_servers: Sequence[MCPServer] = (),
) -> None:
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

                message_history = await _stream(agent, prompt, markdown, message_history)
        except EOFError:
            return


async def _stream(
    agent: Agent, prompt: str, markdown: bool, message_history: list[ModelMessage] | None
) -> list[ModelMessage]:
    async with agent.iter(prompt, message_history=message_history) as run:
        async for node in run:
            if Agent.is_model_request_node(node):
                async with node.stream(run.ctx) as request_stream:
                    await render(request_stream.stream_output(), markdown)
            elif Agent.is_call_tools_node(node):
                async with node.stream(run.ctx) as tool_stream:
                    async for event in tool_stream:
                        if isinstance(event, FunctionToolCallEvent):
                            console.print(f"[yellow]Tool {event.part.tool_name} {event.part.args}")

        return run.result.new_messages() if run.result else []
