# Copyright (C) 2025 Andrew Wason
# SPDX-License-Identifier: AGPL-3.0-or-later

import asyncio
import json
from collections.abc import Sequence

import click
from dotenv import load_dotenv
from pydantic_ai.messages import ModelMessagesTypeAdapter
from pydantic_ai.models import KnownModelName

from .chat import chat
from .tools import load_mcp_servers


@click.command()
@click.option(
    "--model",
    "-m",
    show_default=True,
    default="openai:gpt-4o-mini",
    help="LLM model to use.",
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
    "--tools",
    "-t",
    type=click.Path(dir_okay=False),
    help="Path to tools yaml file",
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
    tools: str | None,
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
            mcp_servers=load_mcp_servers(tools),
        )
    )
