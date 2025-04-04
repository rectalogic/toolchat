# Copyright (C) 2025 Andrew Wason
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import enum
import json
import mimetypes
import readline  # for input()  # noqa: F401
from collections.abc import Sequence
from pathlib import Path

import httpx
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServer
from pydantic_ai.messages import (
    AudioUrl,
    BinaryContent,
    DocumentUrl,
    FunctionToolCallEvent,
    ImageUrl,
    ModelMessage,
    UserContent,
)
from pydantic_ai.models import KnownModelName
from pydantic_core import to_jsonable_python

from .render import console, render

mimetypes.init()


class Command(enum.StrEnum):
    MULTILINE = "/multi"
    ATTACH_IMAGE = "/image"
    ATTACH_AUDIO = "/audio"
    ATTACH_DOCUMENT = "/document"
    ATTACH_FILE = "/file"
    SAVE = "/save"
    HELP = "/help"
    QUIT = "/quit"

    @classmethod
    def from_value(cls, value: str) -> Command | None:
        try:
            return Command(value)
        except ValueError:
            return None


def process_attachment(file_or_url: str) -> BinaryContent | None:
    if "://" not in file_or_url:
        path = Path(file_or_url)
        try:
            mime = mimetypes.guess_type(file_or_url, strict=False)[0] or "application/octet-stream"
            return BinaryContent(data=path.read_bytes(), media_type=mime)
        except Exception as e:
            console.print(f"[red]Enter valid file path: {e}")
            return None
    else:
        response = httpx.get(file_or_url)
        if not response.is_success:
            console.print("[red]Enter valid url")
            return None
        return BinaryContent(
            data=response.content, media_type=response.headers.get("content-type", "application/octet-stream")
        )


def handle_command(command: Command, message_history: list[ModelMessage] | None) -> UserContent | None:
    match command:
        case Command.SAVE:
            path = input("json path>> ")
            if not path:
                console.print("[red]Enter a file path to save history to")
            try:
                with open(path, "w") as f:
                    json.dump(to_jsonable_python(message_history), f, indent=2)
            except Exception as e:
                console.print(f"[ref]Failed to save: {e}")
        case Command.HELP:
            console.print(f"[yellow]{Command.MULTILINE} - enter multiline mode, enter again to exit")
            console.print(f"[yellow]{Command.SAVE} - save chat history")
            console.print(f"[yellow]{Command.ATTACH_IMAGE} - add an image attachment to the current prompt")
            console.print(f"[yellow]{Command.ATTACH_AUDIO} - add an audio attachment to the current prompt")
            console.print(f"[yellow]{Command.ATTACH_DOCUMENT} - add a document attachment to the current prompt")
            console.print(f"[yellow]{Command.ATTACH_FILE} - add a file attachment to the current prompt")
            console.print(f"[yellow]{Command.HELP} - this message")
            console.print(f"[yellow]{Command.QUIT} - quit (also Ctrl-D)")
        case Command.ATTACH_IMAGE:
            url = input("image url>> ")
            return ImageUrl(url=url)
        case Command.ATTACH_AUDIO:
            url = input("audio url>> ")
            return AudioUrl(url=url)
        case Command.ATTACH_DOCUMENT:
            url = input("document url>> ")
            return DocumentUrl(url=url)
        case Command.ATTACH_FILE:
            url = input("file>> ")
            return process_attachment(url)
        case c:
            raise RuntimeError(f"Unhandled command {c}")


async def chat(
    model: KnownModelName,
    markdown: bool,
    message_history: list[ModelMessage] | None,
    system_prompt: str | Sequence[str] = (),
    mcp_servers: Sequence[MCPServer] = (),
) -> None:
    agent = Agent(model, system_prompt=system_prompt, mcp_servers=mcp_servers)

    console.print(f"[green]ToolChat - Ctrl-D or {Command.QUIT} to quit")
    console.print(
        f"[green]Enter {Command.MULTILINE} to enter and exit multiline mode, {Command.HELP} for more commands"
    )

    async with agent.run_mcp_servers():
        prompts: list[UserContent] = []
        try:
            while True:
                prompt = input("> ")
                command = Command.from_value(prompt)
                if command is None:
                    prompts.append(prompt)
                elif command is Command.QUIT:
                    return
                elif command is Command.MULTILINE:
                    lines: list[str] = []
                    while (line := input(". ")) != Command.MULTILINE:
                        lines.append(line)
                    prompts.append("\n".join(lines))
                else:
                    new_prompt = handle_command(command, message_history)
                    if new_prompt is not None:
                        prompts.append(new_prompt)
                    continue

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
                            console.print(f"[dim]Tool {event.part.tool_name} {event.part.args}")

        return run.result.all_messages() if run.result else []
