Modify src/helpdesk_bot.py to add RAG (Red/Amber/Green) threshold
indicators to the metrics output.

Thresholds:
- Guardrail time: GREEN < 10ms, AMBER < 50ms, RED >= 50ms
- Classification time: GREEN < 500ms, AMBER < 1000ms, RED >= 1000ms
- Sonnet time: GREEN < 3s, AMBER < 5s, RED >= 5s
- Cost per message: GREEN < $0.005, AMBER < $0.01, RED >= $0.01
- Fallback rate: GREEN < 2%, AMBER < 5%, RED >= 5%

Display the RAG status as colored [GREEN], [AMBER], or [RED] text
next to each metric value using ANSI colors (green, yellow, red).

Apply to both per-message metrics and any summary output.
