Create src/cost_comparison.py — runs the same set of 20 messages
through TWO architectures and compares the results.

Pass 1 — Single Model (Chapter 1 style):
Every message goes directly to Claude Sonnet. No guardrails, no
classification, no routing. Measure cost and latency for each.

Pass 2 — Multi-Model (current system):
Full pipeline: guardrails → Haiku classifier → route → Sonnet
or canned response. Measure cost and latency for each.

Use the same 20 messages for both passes (same mix as run_full_stack.py).

Print a side-by-side comparison report:
- Single-model total cost vs multi-model total cost
- Savings: dollar amount and percentage
- Per-route breakdown: how many avoided Sonnet
- Latency comparison: mean total time for each approach
- Daily projection (1000 msg/day): monthly cost single vs multi
- Monthly savings estimate

Show the most dramatic individual comparisons:
- "Hello!" — single model cost vs multi model cost (should be ~15-20x)
- Prompt injection — single model cost vs $0.00

Color-coded ANSI output. Plain text, no markdown.
Make the savings numbers BIG and obvious — this is the payoff.
