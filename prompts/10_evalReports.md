Two things:

1) Modify src/helpdesk_bot.py to add a --metrics-report flag. When the
user exits (quit/exit/Ctrl+C), print a summary evaluation report showing:
- Total messages processed
- Route distribution (count and percentage per route type)
- Latency stats: mean, median, P95, P99 for each stage
- Cost breakdown: total, mean per message, Haiku vs Sonnet split
- Safety stats: attacks blocked, PII items redacted
- Reliability: fallback rate, average confidence
- RAG indicators on all stats

Format as a bordered terminal report with section headers. Use ANSI
colors for RAG indicators.

2) Create src/test_multi_model.py — a batch evaluation script that:
- Sends a predefined set of test messages through the full pipeline
- Mix: 4 product questions, 2 greetings, 2 off-topic, 1 complex,
  2 adversarial, 1 with PII
- Collects metrics on each
- Prints the same summary report at the end
- Color-coded terminal output, plain text (no markdown)

Usage: python src/test_multi_model.py
