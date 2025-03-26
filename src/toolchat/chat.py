# Copyright (C) 2025 Andrew Wason
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import enum
import readline  # for input()  # noqa: F401
from collections.abc import Sequence

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServer
from pydantic_ai.messages import AudioUrl, DocumentUrl, FunctionToolCallEvent, ImageUrl, ModelMessage, UserContent
from pydantic_ai.models import KnownModelName

from .render import console, render

# type Renderer = Callable(response: AsyncIterator[str]) -> CoroutineType[Any, Any, str]


class Command(enum.StrEnum):
    MULTILINE = "!multi"
    ATTACH_IMAGE = "!image"
    ATTACH_AUDIO = "!audio"
    ATTACH_DOCUMENT = "!document"
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
    console.print(f"[green]Enter {Command.MULTILINE} to enter/exit multiline mode, {Command.HELP} for more commands")

    async with agent.run_mcp_servers():
        message_history = None
        prompts: list[UserContent] = []

        try:
            while True:
                prompt = input("> ")

                if prompt == Command.QUIT:
                    return
                elif prompt == Command.HELP:
                    console.print(f"[yellow]{Command.MULTILINE} - enter multiline mode, enter again to exit")
                    console.print(f"[yellow]{Command.ATTACH_IMAGE} - add an image attachment to the current prompt")
                    console.print(f"[yellow]{Command.ATTACH_AUDIO} - add an audio attachment to the current prompt")
                    console.print(
                        f"[yellow]{Command.ATTACH_DOCUMENT} - add a document attachment to the current prompt"
                    )
                    console.print(f"[yellow]{Command.HELP} - this message")
                    console.print(f"[yellow]{Command.QUIT} - quit (also Ctrl-D)")
                    continue
                elif prompt == Command.ATTACH_IMAGE:
                    url = input("image url>> ")
                    prompts.append(ImageUrl(url=url))
                    continue
                elif prompt == Command.ATTACH_AUDIO:
                    url = input("audio url>> ")
                    prompts.append(AudioUrl(url=url))
                    continue
                elif prompt == Command.ATTACH_DOCUMENT:
                    url = input("document url>> ")
                    prompts.append(DocumentUrl(url=url))
                    continue
                elif prompt == Command.MULTILINE:
                    lines: list[str] = []
                    while (line := input(". ")) != Command.MULTILINE:
                        if line in Command:
                            console.print(
                                "[red]Commands not accept in multiline mode,"
                                f" enter {Command.MULTILINE} to exit multiline"
                            )
                            continue
                        lines.append(line)
                    prompts.append("\n".join(lines))
                else:
                    prompts.append(prompt)

                message_history = await _stream(agent, prompts, markdown, message_history)
                prompts = []
        except EOFError:
            return


async def _stream(
    agent: Agent, prompts: list[UserContent], markdown: bool, message_history: list[ModelMessage] | None
) -> list[ModelMessage]:
    async with agent.iter(prompts, message_history=message_history) as run:
        async for node in run:
            if Agent.is_model_request_node(node):
                async with node.stream(run.ctx) as request_stream:
                    await render(request_stream.stream_output(), markdown)
            elif Agent.is_call_tools_node(node):
                async with node.stream(run.ctx) as tool_stream:
                    async for event in tool_stream:
                        if isinstance(event, FunctionToolCallEvent):
                            console.print(f"[grey0]Tool {event.part.tool_name} {event.part.args}")

        return run.result.all_messages() if run.result else []
