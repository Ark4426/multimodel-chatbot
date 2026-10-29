Modify src/helpdesk_bot.py to add PII detection as the FIRST step
in the message pipeline — before classification, before routing.

PII detection should:
- Use regex to detect email addresses and phone numbers
- Phone formats to catch: xxx-xxx-xxxx, (xxx) xxx-xxxx,
  xxx.xxx.xxxx, +1xxxxxxxxxx, +1 xxx xxx xxxx
- If PII found: redact it (replace with [EMAIL REDACTED] or
  [PHONE REDACTED]), print a privacy notice in cyan, then
  continue processing with the redacted message
- If no PII: continue normally

In --debug mode, print a dim gray guardrail line BEFORE the
classification line showing: "PII Detection" result, number of
items found, and processing time in milliseconds.

Do NOT block messages with PII — redact and continue. Blocking
is for unsafe requests (next video).
