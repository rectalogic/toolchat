# Copyright (C) 2025 Andrew Wason
# SPDX-License-Identifier: AGPL-3.0-or-later
import os
import typing as t

import yaml
from pydantic_ai.mcp import MCPServer, MCPServerHTTP, MCPServerStdio
from pydantic_ai.tools import ToolDefinition


# Post-process schema so it works with Gemini
# https://github.com/pydantic/pydantic-ai/issues/1250
class MCPServerMixin:
    def _list_tools_schema(self, tools: list[ToolDefinition]) -> list[ToolDefinition]:
        return [self._modify_schema(tool) for tool in tools]

    def _modify_schema(self, tool: ToolDefinition) -> ToolDefinition:
        tool.parameters_json_schema.pop("$schema", None)
        return tool


class MCPServerStdioSchema(MCPServerMixin, MCPServerStdio):
    @t.override
    async def list_tools(self) -> list[ToolDefinition]:
        return self._list_tools_schema(await super().list_tools())

    async def __aexit__(self, exc_type, exc_value, traceback) -> bool | None:
        return await super().__aexit__(exc_type, exc_value, traceback)


class MCPServerHTTPSchema(MCPServerMixin, MCPServerHTTP):
    @t.override
    async def list_tools(self) -> list[ToolDefinition]:
        return self._list_tools_schema(await super().list_tools())


def load_mcp_servers(path: str | None) -> list[MCPServer]:
    if not path or not os.path.exists(path):
        return []
    with open(path) as f:
        return [_load_mcp_server(s) for s in yaml.safe_load(f)]


def _load_mcp_server(d: dict) -> MCPServer:
    server = d.get("server")
    if not server:
        raise RuntimeError(f"Missing MCPServer definition {d}")
    match d.get("type"):
        case "stdio":
            return MCPServerStdioSchema(**server)
        case "http":
            return MCPServerHTTPSchema(**server)
        case x:
            raise RuntimeError(f"Invalid MCPServer type {x}")
