# Copyright (C) 2025 Andrew Wason
# SPDX-License-Identifier: AGPL-3.0-or-later

from collections.abc import AsyncIterator

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

console = Console()


async def render_text(response: AsyncIterator[str]) -> str:
    current = []
    async for chunk in response:
        print(chunk, end="", flush=True)
        current.append(chunk)
    return "".join(current)


async def render_markdown(response: AsyncIterator[str]) -> str:
    current = ""
    with Live(auto_refresh=False, console=console) as live:
        async for chunk in response:
            current += chunk
            markdown = Markdown(current)
            live.update(markdown, refresh=True)
    return current
