# ToolChat

Chat with LLMs using [MCP servers](https://modelcontextprotocol.io/docs/concepts/tools).

Configure MCP tool servers in a YAML file and provide path to `--tool-servers`,
enable specific tools with `--enable-tool-server`.
See [sample-tools.yml](sample-tools.yml) for format.

If the model is multimodal you can also include images, documents etc. in your prompt.
See the `/help` command for details.

## Example

Use AWS documentation tool with Gemini Pro 2.5 to search AWS docs:

```sh-session
$ uv run toolchat --model google-gla:gemini-2.5-pro-exp-03-25 --tool-servers sample-tools.yml --enable-tool-server awslabs.aws-documentation-mcp-server
ToolChat - Ctrl-D or /quit to quit
Enter /multi to enter and exit multiline mode, /help for more commands
> look up documentation on S3 bucket naming rule. cite your sources
Okay, I can help with that. I will search for the S3 bucket naming rules
documentation and provide a summary along with the source URL.
```
_`Tool search_documentation {'search_phrase': 'S3 bucket naming rules', 'limit':
1}`_
```sh-session
Okay, I found a relevant document. I will now read the content to summarize the
S3 bucket naming rules.
```
_`Tool read_documentation {'url':
'https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html'}`_
```sh-session
Okay, here is a summary of the naming rules for Amazon S3 general purpose
buckets, based on the official AWS documentation:

S3 General Purpose Bucket Naming Rules:

 • Length: Must be between 3 and 63 characters long.
 • Characters: Can only contain lowercase letters (a-z), numbers (0-9), periods
   (.), and hyphens (-).
 • Start/End: Must begin and end with a letter or number.
 ...[elided]
```
