Modify src/helpdesk_bot.py to add confidence-based fallback routing.

Rules:
- If classifier confidence >= 0.7: route based on intent (existing
  routing logic from 02_04)
- If classifier confidence < 0.7: ignore the intent and send to Sonnet
  regardless (safe fallback — let the smart model handle ambiguity)

In --debug mode, show the route as one of:
- "route=canned" (high confidence, canned response)
- "route=classified→sonnet" (high confidence, sent to Sonnet by intent)
- "route=fallback→sonnet" (low confidence, fell back to Sonnet)

Keep all existing colored output and debug formatting.
