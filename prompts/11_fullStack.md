Create src/run_full_stack.py — a full integration test for the
TaskFlow help desk pipeline.

Send 20+ messages with realistic distribution:
- 8 product questions (varied: features, pricing, comparisons, how-to)
- 5 greetings / small talk
- 3 off-topic (weather, sports, random)
- 2 complex enterprise questions
- 2 adversarial (prompt injection, jailbreak)
- 2 with PII (email, phone)

Process each through the full pipeline (import from helpdesk_bot.py
or reimplement: guardrails → classify → route → generate).

Show a live dashboard that updates after each message:
- Progress: [12/22] ████████░░░░ 55%
- Route counts updating: sonnet: 4 | canned: 5 | blocked: 2 | redact: 1
- Running cost: $0.0234
- Health: all GREEN or show any AMBER/RED

After all messages, print a full evaluation report with:
- Route distribution with percentages and bar chart
- Latency stats (mean, P95, P99) per stage
- Cost breakdown (Haiku vs Sonnet, total, mean per message)
- Safety stats (blocked, PII redacted)
- Fallback rate with RAG indicator
- All with colored ANSI output, plain text, no markdown
