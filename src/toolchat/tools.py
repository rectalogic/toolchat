# Copyright (C) 2025 Andrew Wason
# SPDX-License-Identifier: AGPL-3.0-or-later
import os
from pydantic import BaseModel
from pydantic_ai.mcp import MCPServer, MCPServerHTTP, MCPServerStdio
import yaml


def load_mcp_servers(path: str) -> list[MCPServer]:
    #XXX not finding relative path
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
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
