"""Single-model vs multi-model: same messages through both architectures, compare cost and latency.

Usage: python src/cost_comparison.py
"""
import contextlib
import io
import json
import os
import statistics
import time

from helpdesk_bot import (ask, tokens, process_message, INPUT_PRICE, OUTPUT_PRICE, CLAUDE,
                          BOLD, CYAN, DIM, RESET)
from run_full_stack import MESSAGES

GREEN, YELLOW, RED = "\033[1;32m", "\033[1;33m", "\033[1;31m"
MESSAGES_PER_DAY, DAYS = 1000, 30
WIDTH = 72

# 5-row block font for the headline numbers
FONT = {
    "0": ["███", "█ █", "█ █", "█ █", "███"], "1": [" █ ", "██ ", " █ ", " █ ", "███"],
    "2": ["███", "  █", "███", "█  ", "███"], "3": ["███", "  █", "███", "  █", "███"],
    "4": ["█ █", "█ █", "███", "  █", "  █"], "5": ["███", "█  ", "███", "  █", "███"],
    "6": ["███", "█  ", "███", "█ █", "███"], "7": ["███", "  █", "  █", "  █", "  █"],
    "8": ["███", "█ █", "███", "█ █", "███"], "9": ["███", "█ █", "███", "  █", "███"],
    ".": ["   ", "   ", "   ", "   ", " █ "], ",": ["   ", "   ", "   ", " █ ", "█  "],
    "%": ["█  █", "  █ ", " █  ", "█   ", "█  █"], "$": [" ███", "█ █ ", " ███", "  ██", "███ "],
    " ": ["  ", "  ", "  ", "  ", "  "],
}


def big(text, color):
    for row in range(5):
        print("   " + color + " ".join(FONT[c][row] for c in text) + RESET)


def single_model_pass():
    """Chapter 1 style: every message straight to Sonnet."""
    results = []
    for i, (_, message) in enumerate(MESSAGES, 1):
        print(f"{DIM}  [{i}/{len(MESSAGES)}] {message[:60]}{RESET}")
        start = time.perf_counter()
        try:
            data = ask(message, None)
        except (RuntimeError, json.JSONDecodeError) as e:
            print(f"{RED}  error: {e}{RESET}")
            results.append({"cost": 0.0, "ms": (time.perf_counter() - start) * 1000, "error": True})
            continue
        in_tok, out_tok = tokens(data)
        results.append({"cost": in_tok * INPUT_PRICE + out_tok * OUTPUT_PRICE,
                        "ms": (time.perf_counter() - start) * 1000})
    return results


def multi_model_pass():
    results = []
    for i, (_, message) in enumerate(MESSAGES, 1):
        print(f"{DIM}  [{i}/{len(MESSAGES)}] {message[:60]}{RESET}")
        with contextlib.redirect_stdout(io.StringIO()):  # hide replies
            _, m = process_message(message, None)
        results.append({"cost": m["haiku_cost"] + m["sonnet_cost"], "ms": m["total_ms"], "route": m["route"]})
    return results


def line(char="─"):
    print(CYAN + char * WIDTH + RESET)


def header(title):
    print()
    line("═")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    line("═")


def main():
    os.system("")  # ANSI colors on Windows
    if not CLAUDE:
        raise SystemExit("claude CLI not found on PATH - install Claude Code and log in first")

    n = len(MESSAGES)
    print(f"{BOLD}Pass 1: single model (every message -> Sonnet), {n} messages{RESET}")
    single = single_model_pass()
    print(f"{BOLD}Pass 2: multi model (guardrails -> Haiku -> route), {n} messages{RESET}")
    multi = multi_model_pass()

    s_total = sum(r["cost"] for r in single)
    m_total = sum(r["cost"] for r in multi)
    saved = s_total - m_total
    pct = saved / s_total if s_total else 0
    s_monthly = s_total / n * MESSAGES_PER_DAY * DAYS
    m_monthly = m_total / n * MESSAGES_PER_DAY * DAYS

    header("SINGLE MODEL vs MULTI MODEL")
    print(f"  {'':<26}{'SINGLE (Sonnet)':>20}{'MULTI-MODEL':>20}")
    line()
    print(f"  {'total cost':<26}{RED}{'$' + format(s_total, '.4f'):>20}{RESET}{GREEN}{'$' + format(m_total, '.4f'):>20}{RESET}")
    print(f"  {'mean cost / message':<26}{RED}{'$' + format(s_total / n, '.5f'):>20}{RESET}"
          f"{GREEN}{'$' + format(m_total / n, '.5f'):>20}{RESET}")
    s_ms = statistics.mean(r["ms"] for r in single)
    m_ms = statistics.mean(r["ms"] for r in multi)
    faster = GREEN if m_ms < s_ms else YELLOW
    print(f"  {'mean total latency':<26}{s_ms:>18.0f}ms{faster}{m_ms:>18.0f}ms{RESET}")
    print(f"  {'Sonnet calls':<26}{n:>20}{sum('sonnet' in r['route'] for r in multi):>20}")

    header("ROUTES (multi-model) - who avoided Sonnet")
    routes = {}
    for r in multi:
        routes[r["route"]] = routes.get(r["route"], 0) + 1
    for route, count in sorted(routes.items(), key=lambda kv: -kv[1]):
        avoided = "sonnet" not in route
        mark = f"{GREEN}avoided Sonnet{RESET}" if avoided else f"{DIM}used Sonnet{RESET}"
        print(f"  {route:<22}{count:>4}  {count / n:>6.1%}  {'█' * round(count / n * 25):<26}{mark}")
    avoided = sum("sonnet" not in r["route"] for r in multi)
    print(f"\n  {BOLD}{GREEN}{avoided} of {n} messages ({avoided / n:.0%}) never touched Sonnet{RESET}")

    header("HEAD TO HEAD")
    for label, idx in [("\"Hello!\"", next(i for i, (_, msg) in enumerate(MESSAGES) if msg == "Hello!")),
                       ("Prompt injection", next(i for i, (c, _) in enumerate(MESSAGES) if c == "adversarial"))]:
        s, m = single[idx]["cost"], multi[idx]["cost"]
        ratio = "infinitely cheaper (no API call)" if m == 0 else f"{s / m:.1f}x cheaper"
        print(f"  {BOLD}{label:<18}{RESET} single {RED}${s:.6f}{RESET}  ->  multi {GREEN}${m:.6f}{RESET}"
              f"   {BOLD}{GREEN}{ratio}{RESET}")
        print(f"  {DIM}{'':<18} route: {multi[idx]['route']}{RESET}")

    header(f"PROJECTION: {MESSAGES_PER_DAY:,} messages/day x {DAYS} days")
    print(f"  single model:  {RED}${s_monthly:>10,.2f} / month{RESET}")
    print(f"  multi model:   {GREEN}${m_monthly:>10,.2f} / month{RESET}")
    print(f"  per year:      {RED}${s_monthly * 12:>10,.2f}{RESET}  vs  {GREEN}${m_monthly * 12:,.2f}{RESET}")

    header("THE PAYOFF")
    color = GREEN if saved > 0 else RED
    print(f"\n  {BOLD}Saved on this run: ${saved:.4f}{RESET}\n")
    print(f"  {BOLD}MONTHLY SAVINGS{RESET}")
    big(f"${s_monthly - m_monthly:,.0f}", color)
    print(f"\n  {BOLD}COST REDUCTION{RESET}")
    big(f"{pct:.0%}", color)
    print()
    line("═")
    print(f"{DIM}  Costs use list prices on tokens reported by the claude CLI (Pro login), which adds\n"
          f"  some prompt overhead per call. Run it with an API key for production numbers.{RESET}")


if __name__ == "__main__":
    main()
