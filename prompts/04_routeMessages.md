Modify src/helpdesk_bot.py to add routing based on the classifier's intent.

Routing rules:
- "greeting" → canned response: "Hi there! How can I help you with
  TaskFlow today?" (no Sonnet call)
- "off_topic" → canned response: "I can only help with TaskFlow
  questions. For other inquiries, contact support@taskflow.com"
  (no Sonnet call)
- "adversarial" → canned response: "I'm not able to help with that
  request." (no Sonnet call)
- "product_question" → send to Sonnet (existing behavior)
- "complex" → send to Sonnet (existing behavior)

In --debug mode, show the route taken: "route=canned" or "route=sonnet"
in the classification debug line. When a canned response is used,
don't print a Sonnet debug line since Sonnet was never called.

Keep the colored output: green bold "You:", cyan bold "TaskFlow:".
