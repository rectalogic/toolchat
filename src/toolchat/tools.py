# Copyright (C) 2025 Andrew Wason
# SPDX-License-Identifier: AGPL-3.0-or-later
import os
from pydantic import BaseModel
import yaml
from mcp import  StdioServerParameters



def load_tools(path: str) -> list[StdioServerParameters]:
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return [StdioServerParameters(**s) for s in yaml.safe_load(f)]
