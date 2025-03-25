# Copyright (C) 2025 Andrew Wason
# SPDX-License-Identifier: AGPL-3.0-or-later

import asyncio
import os
import pathlib
import typing as t
from collections.abc import Callable, AsyncIterator

import click
from dotenv import load_dotenv
from pydantic_ai.models import KnownModelName

from . import chat
from .tools import load_tools


@click.command()
@click.option(
    "--model",
    "-m",
    show_default=True,
    # XXX validate KnownModelName
    default="openai:gpt-4o-mini",
    help="LLM model to use.",
)
@click.option(
    "--dotenv",
    "-e",
    type=click.Path(dir_okay=False),
    default=".env",
    help="Load environment variables (API keys) from a .env file.",
)
@click.option(
    "--tools",
    type=click.Path(dir_okay=False),
    help="Path to tools yaml file - ./tools.yaml if it exists",
    show_default=True,
    default="./tools.yaml",
)
@click.option("--system-message", "-s", help="System message.")
@click.option("--markdown/--no-markdown", help="Render LLM responses as Markdown.", default=True)
@click.version_option()
def cli(
    model: KnownModelName,
    dotenv: str,
    tools: str,
    system_message: str | None,
    markdown: bool,
) -> None:
    load_dotenv(dotenv)

    asyncio.run(chat.Chat(
        model,
        tool_servers=load_tools(tools),
    ).chat(markdown, system_message=system_message))
