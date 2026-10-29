"""Send one message to Haiku, Sonnet and Opus and compare latency, tokens and cost.

Usage: python src/compare_models.py "What features does Pro include?"
"""
import os
import sys
import time

from helpdesk_bot import ask, CYAN, DIM, RESET

GREEN, YELLOW, RED, BOLD = "\033[32m", "\033[33m", "\033[31m", "\033[1m"

# model id -> ($ per input token, $ per output token)
# ponytail: claude-sonnet-4-20250514 is retired and claude-opus-4-20250114 doesn't exist,
# so the current Sonnet/Opus are used with the course's prices.
MODELS = {
    "claude-haiku-4-5-20251001": (1 / 1e6, 5 / 1e6),
    "claude-sonnet-5-5": (3 / 1e6, 15 / 1e6),
    "claude-opus-5-5": (15 / 1e6, 75 / 1e6),
}


def run(model, message):
    start = time.perf_counter()
    try:
        data = ask(message, None, model)
    except RuntimeError as e:
        return {"model": model, "error": str(e)}
    latency = time.perf_counter() - start
    u = data["usage"]
    in_tok = u["input_tokens"] + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
    out_tok = u["output_tokens"]
    in_price, out_price = MODELS[model]
    return {"model": model, "latency": latency, "in": in_tok, "out": out_tok,
            "cost": in_tok * in_price + out_tok * out_price,
            "text": " ".join(data["result"].replace("**", "").split())}


def main():
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python src/compare_models.py "your message"')
    message = " ".join(sys.argv[1:])
    os.system("")  # ANSI colors on Windows

    results = []
    for model in MODELS:
        print(f"{DIM}asking {model}...{RESET}")
        results.append(run(model, message))

    ok = [r for r in results if "error" not in r]
    cheapest = min(ok, key=lambda r: r["cost"])["model"] if ok else None
    priciest = max(ok, key=lambda r: r["cost"])["model"] if ok else None

    print(f"\n{BOLD}{CYAN}Message:{RESET} {message}\n")
    header = f"{'Model':<28}{'Latency':>9}{'In':>7}{'Out':>7}{'Cost':>11}"
    print(BOLD + header + RESET)
    print("-" * len(header))
    for r in results:
        if "error" in r:
            print(f"{RED}{r['model']:<28} ERROR: {r['error'][:100]}{RESET}")
            continue
        color = GREEN if r["model"] == cheapest else RED if r["model"] == priciest else YELLOW
        print(f"{color}{r['model']:<28}{r['latency']:>8.2f}s{r['in']:>7}{r['out']:>7}  ${r['cost']:>8.5f}{RESET}")
    print(f"{DIM}green = cheapest | red = most expensive{RESET}\n")

    print(f"{BOLD}{CYAN}Responses (first 150 chars){RESET}")
    for r in ok:
        print(f"{BOLD}{r['model']}{RESET}\n  {r['text'][:150]}{'...' if len(r['text']) > 150 else ''}\n")


if __name__ == "__main__":
    main()
