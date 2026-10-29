"""Health report from logs/session.jsonl.

Usage: python src/monitor.py
"""
import json
import os
import statistics
from collections import Counter

from helpdesk_bot import LOG_DIR, RAG_COLORS, ANSI_RE, rag_level, percentile, BOLD, CYAN, DIM, RESET

WIDTH = 72


def tag(metric, value):
    level = rag_level(metric, value)
    return f" {RAG_COLORS[level]}[{level}]{RESET}"


def read_jsonl(path):
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def section(title):
    print(f"\n{BOLD}{CYAN}{title}{RESET}")
    print(CYAN + "─" * WIDTH + RESET)


def main():
    os.system("")  # ANSI colors on Windows
    log_file = LOG_DIR / "session.jsonl"
    entries = read_jsonl(log_file)
    if not entries:
        print(f"{BOLD}No log data yet.{RESET} Expected {log_file}")
        print("Run the bot to generate some:  python src/helpdesk_bot.py")
        print("or a batch test:               python src/run_full_stack.py")
        return
    flagged = read_jsonl(LOG_DIR / "flagged_for_review.jsonl")
    n = len(entries)

    print(CYAN + "═" * WIDTH + RESET)
    print(f"{BOLD}  TASKFLOW HELP DESK - HEALTH REPORT{RESET}")
    print(f"{DIM}  {entries[0]['timestamp'][:19]}  ->  {entries[-1]['timestamp'][:19]} (UTC){RESET}")
    print(CYAN + "═" * WIDTH + RESET)
    print(f"  Total messages processed: {BOLD}{n}{RESET}")

    section("ROUTE DISTRIBUTION")
    for route, count in Counter(e["route"] for e in entries).most_common():
        print(f"  {str(route):<24}{count:>5}  {count / n:>6.1%}  {CYAN}{'█' * round(count / n * 30)}{RESET}")

    section("COST")
    costs = [e["cost_total"] for e in entries]
    mean = statistics.mean(costs)
    print(f"  total:            ${sum(costs):.6f}")
    print(f"  mean per message: ${mean:.6f}{tag('cost', mean)}")
    print(f"  haiku / sonnet:   ${sum(e['cost_haiku'] for e in entries):.6f} / ${sum(e['cost_sonnet'] for e in entries):.6f}")
    if n >= 4:
        # trend: mean cost of the older half vs the newer half of the log
        half = n // 2
        old, new = statistics.mean(costs[:half]), statistics.mean(costs[half:])
        change = (new - old) / old if old else 0
        color = RAG_COLORS["RED"] if change > 0.10 else RAG_COLORS["AMBER"] if change > 0 else RAG_COLORS["GREEN"]
        direction = "increasing" if change > 0 else "decreasing" if change < 0 else "flat"
        print(f"  trend:            {color}{direction} ({change:+.1%}){RESET}  "
              f"{DIM}older half ${old:.6f} -> newer half ${new:.6f}{RESET}")
    else:
        print(f"  trend:            {DIM}need 4+ messages{RESET}")

    section(f"LATENCY (ms)  {'mean':>16}{'P95':>20}")
    for label, key, metric in [("guardrail", "latency_guardrail_ms", "guardrail_ms"),
                               ("classification", "latency_classify_ms", "classify_ms"),
                               ("sonnet", "latency_sonnet_ms", "sonnet_ms"),
                               ("total", "latency_total_ms", None)]:
        values = [e[key] for e in entries if e[key] is not None]
        if not values:
            print(f"  {label:<16}{'n/a':>14}")
            continue
        avg, p95 = statistics.mean(values), percentile(values, 95)
        avg_tag, p95_tag = (tag(metric, avg), tag(metric, p95)) if metric else ("", "")
        pad = " " * (9 - len(ANSI_RE.sub("", avg_tag)))  # tags carry invisible ANSI codes
        print(f"  {label:<16}{avg:>12.2f}{avg_tag}{pad}{p95:>12.2f}{p95_tag}")

    section("SAFETY")
    print(f"  attacks blocked:    {sum(e['was_blocked'] for e in entries)}")
    print(f"  PII items redacted: {sum(e['pii_found'] for e in entries)} "
          f"{DIM}(in {sum(e['pii_found'] > 0 for e in entries)} messages){RESET}")

    section("RELIABILITY")
    classified = [e for e in entries if e["confidence"] is not None]
    if classified:
        fallback_rate = sum(e["was_fallback"] for e in classified) / len(classified)
        flagged_rate = len(flagged) / len(classified)
        avg_conf = statistics.mean(e["confidence"] for e in classified)
        print(f"  fallback rate:      {fallback_rate:.1%} ({sum(e['was_fallback'] for e in classified)}/{len(classified)})"
              f"{tag('fallback_rate', fallback_rate)}")
        print(f"  flagged for review: {flagged_rate:.1%} ({len(flagged)}/{len(classified)}){tag('flagged_rate', flagged_rate)}")
        print(f"  average confidence: {avg_conf:.2f}{tag('confidence', avg_conf)}")
    else:
        print("  no messages reached the classifier")
    if flagged:
        print(f"\n  {DIM}Latest flagged for review:{RESET}")
        for e in flagged[-3:]:
            print(f"  {DIM}- [{e['confidence']:.2f} {e['intent']}] {e['redacted_message'] or e['original_message']}{RESET}")
    print(CYAN + "═" * WIDTH + RESET)


if __name__ == "__main__":
    main()
