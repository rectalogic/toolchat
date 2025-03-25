# Copyright (C) 2025 Andrew Wason
# SPDX-License-Identifier: AGPL-3.0-or-later

from contextlib import AsyncExitStack
import itertools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic_mcp import mcptools
from pydantic_ai import Tool

class MCPClient:
    def __init__(self, servers: list[StdioServerParameters]):
        self.exit_stack = AsyncExitStack()
        self.servers = servers

    async def close(self):
        await self.exit_stack.aclose();

    async def list_tools(self)-> list[Tool]:
        tools = [await self._connect(server) for server in self.servers]
        return list(itertools.chain.from_iterable(tools))

    async def _connect(self, server: StdioServerParameters) -> list[Tool]:
        server_params = StdioServerParameters(
            command=server.command,
            args=server.args,
        )

        read, write = await self.exit_stack.enter_async_context(stdio_client(server_params))
        session = await self.exit_stack.enter_async_context(ClientSession(read, write))

        await session.initialize()

        return await mcptools(session)
