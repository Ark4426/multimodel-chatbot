Create src/compare_models.py that takes a message as a command-line
argument and sends it to all three Claude models: claude-haiku-4-5-20251001,
claude-sonnet-4-20250514, and claude-opus-4-20250114.

For each model, measure: response time, input tokens, output tokens,
estimated cost (Haiku: $1/M input, $5/M output; Sonnet: $3/M input,
$15/M output; Opus: $15/M input, $75/M output).

Use the same system prompt as our helpdesk bot (TaskFlow product tiers).
Tell the model to respond in plain text, no markdown.

Print a color-coded comparison table showing all three models side by
side: model name, latency, tokens, cost, and first 150 chars of the
response. Green for cheapest, red for most expensive. Use monospace
font and ANSI colors for clean terminal output.

Usage: python src/compare_models.py "What features does Pro include?"
