# Copyright (C) 2025 Andrew Wason
# SPDX-License-Identifier: AGPL-3.0-or-later

from collections.abc import AsyncIterator

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

console = Console()


async def render(response: AsyncIterator[str], markdown: bool = True) -> None:
    with Live(auto_refresh=False, console=console, vertical_overflow="visible") as live:
        async for message in response:
            live.update(Markdown(message) if markdown else message, refresh=True)
