Build a command-line help desk chatbot in src/helpdesk_bot.py for TaskFlow,
a project management tool. Use Claude Sonnet through the Claude Code CLI
(`claude -p`) so it runs on a Claude Pro subscription login. No Anthropic
API key and no `anthropic` package are needed.

How to call the model:
- Run `claude -p "<message>" --output-format json --model sonnet
  --system-prompt "<system prompt>" --tools ""` with subprocess
- Also pass `--setting-sources project --strict-mcp-config` so user-level
  plugins, hooks and MCP servers don't add ~20k tokens to every call
- Find the CLI with shutil.which("claude") and exit with a helpful message
  if it isn't installed
- Keep conversation history by passing `--resume <session_id>` using the
  session_id from the previous JSON response
- Read the reply from "result", tokens from "usage" (count input_tokens +
  cache_creation_input_tokens + cache_read_input_tokens as input), and the
  model name from the "modelUsage" keys
- Treat a non-zero exit code or "is_error": true as an error, print it in
  red and keep the conversation loop running

System prompt with product tiers: Free (5 users, basic boards),
Pro ($12/user/month, unlimited projects, Gantt charts, Slack/GitHub/Jira
integrations, up to 50 users), Enterprise (custom pricing, SSO/SAML,
audit logs, dedicated support, unlimited). Tell the model to respond
in plain text only, no markdown formatting.

Color-coded terminal output: green bold for "You:" prompt, cyan bold
for "TaskFlow:" responses. Call os.system("") at startup so ANSI colors
work in the Windows console. Print a startup banner with the bot name
and model info. Conversation loop that exits on quit or exit.

Debug flag (--debug) that prints a dim gray line after each response
showing: model name, input tokens, output tokens, latency in seconds,
and estimated cost (Sonnet pricing: $3/M input, $15/M output).
Strip any ** markdown from responses before printing.

Note: the Pro subscription has no per-token billing; the cost shown is
what the same tokens would cost on the API. Calls count against your
Pro usage limits.
