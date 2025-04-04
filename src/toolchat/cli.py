# Copyright (C) 2025 Andrew Wason
# SPDX-License-Identifier: AGPL-3.0-or-later

import asyncio
import json
from collections.abc import Sequence

import click
from dotenv import load_dotenv
from pydantic_ai.messages import ModelMessagesTypeAdapter
from pydantic_ai.models import KnownModelName
from typing_inspection.introspection import get_literal_values

from .chat import chat
from .tools import load_mcp_servers


def list_models(ctx: click.Context, param: click.Option, value: bool):
    if not value:
        return
    click.echo("\n".join(get_literal_values(KnownModelName.__value__)))
    ctx.exit(0)


@click.command()
@click.option(
    "--model",
    "-m",
    show_default=True,
    default="openai:gpt-4o-mini",
    help="LLM model to use.",
)
@click.option(
    "--list-models",
    "-l",
    is_flag=True,
    callback=list_models,
    expose_value=False,
    is_eager=True,
    help="List known LLM models.",
)
@click.option(
    "--dotenv",
    "-e",
    type=click.Path(dir_okay=False),
    default=".env",
    help="Load environment variables (API keys) from a .env file.",
    show_default=True,
)
@click.option(
    "--tool-servers",
    "-t",
    type=click.Path(dir_okay=False),
    help="Path to MCP tool servers yaml file",
)
@click.option(
    "--enable-tool-server",
    "-et",
    multiple=True,
    help="Enable named MCP tool server, all if not specified",
)
@click.option(
    "--history",
    "-h",
    type=click.Path(dir_okay=False),
    help="Path to saved message history file to load on startup",
)
@click.option("--system-prompt", "-s", help="System prompt.", multiple=True, default=())
@click.option("--markdown/--no-markdown", help="Render LLM responses as Markdown.", default=True)
@click.version_option()
def cli(
    model: KnownModelName,
    dotenv: str,
    tool_servers: str | None,
    enable_tool_server: list[str] | None,
    history: str | None,
    system_prompt: Sequence[str],
    markdown: bool,
) -> None:
    load_dotenv(dotenv)
    if history:
        with open(history) as f:
            message_history = ModelMessagesTypeAdapter.validate_python(json.load(f))
    else:
        message_history = None
    asyncio.run(
        chat(
            model,
            markdown,
            message_history=message_history,
            system_prompt=system_prompt,
            mcp_servers=load_mcp_servers(tool_servers, enable_tool_server),
        )
    )
