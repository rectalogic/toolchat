# ToolChat

Chat with AIs using [MCP servers](https://modelcontextprotocol.io/docs/concepts/tools).

```sh-session
$ uv run toolchat --model gpt-4o-mini --tools tools.yml.sample
```

Configure MCP tool servers in a YAML file and provide path to `--tools`.
See [tools.yml.sample](tools.yml.sample) for format.
