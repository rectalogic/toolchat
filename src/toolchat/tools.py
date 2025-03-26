# Copyright (C) 2025 Andrew Wason
# SPDX-License-Identifier: AGPL-3.0-or-later
import os

import yaml
from pydantic_ai.mcp import MCPServer, MCPServerHTTP, MCPServerStdio


def load_mcp_servers(path: str) -> list[MCPServer]:
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [_load_mcp_server(s) for s in yaml.safe_load(f)]


def _load_mcp_server(d: dict) -> MCPServer:
    server = d.get("server")
    if not server:
        raise RuntimeError(f"Missing MCPServer definition {d}")
    match d.get("type"):
        case "stdio":
            return MCPServerStdio(**server)
        case "http":
            return MCPServerHTTP(**server)
        case x:
            raise RuntimeError(f"Invalid MCPServer type {x}")
