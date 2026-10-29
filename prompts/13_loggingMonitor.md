Three changes:

1) Modify src/helpdesk_bot.py to add structured JSON logging.
Every message writes one JSON line to logs/session.jsonl with:
timestamp, message_id, original_message, redacted_message (if PII),
intent, confidence, route, guardrail_action, cost_haiku, cost_sonnet,
cost_total, latency_guardrail_ms, latency_classify_ms,
latency_sonnet_ms, latency_total_ms, was_fallback, was_blocked,
pii_found.
Create the logs/ directory if it doesn't exist.

2) Also in helpdesk_bot.py: if classifier confidence < 0.8, write
the message to logs/flagged_for_review.jsonl with the same fields
plus a "reason": "low_confidence" field. These are messages that
need human review.

3) Create src/monitor.py — reads logs/session.jsonl and generates
a health report:
- Total messages processed
- Route distribution with percentages
- Cost: total, mean, trend (is it increasing?)
- Latency: mean, P95 per stage
- Safety: total blocked, total PII redacted
- Reliability: fallback rate, flagged-for-review rate
- All with RAG color indicators
- If no log file exists, print a helpful message

Color-coded ANSI output, plain text, no markdown.
Usage: python src/monitor.py
