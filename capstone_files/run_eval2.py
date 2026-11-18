#!/usr/bin/env python3
"""
Run the deal-check acceptance scenarios three times and write a before/after log.

Examples:
    python capstone_files/run_eval2.py
    python capstone_files/run_eval2.py --label before
    python capstone_files/run_eval2.py --label after --tries 3
"""

import argparse
import datetime as dt
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config
import agent
from tools import check_deal
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

sys.path.insert(0, str(ROOT / "capstone_files"))
import scenarios as scenario_module


def run_once(scenario, use_trace=True):
    """Run one deal-check scenario once and record the evidence."""
    import trace as trace_module

    record = {
        "error": None,
        "session": None,
        "trace": "",
        "crashed": None,
        "direct_result": None,
        "suggest_outfit_calls": 0,
    }

    try:
        if scenario["kind"] == "tool":
            record["direct_result"] = check_deal(
                scenario["item"], scenario["max_price"]
            )
        else:
            wardrobe = (
                get_empty_wardrobe()
                if scenario["wardrobe"] == "empty"
                else get_example_wardrobe()
            )

            original_search = agent._search
            original_suggest = agent.suggest_outfit

            if scenario.get("synthetic_item") is not None:
                synthetic_item = dict(scenario["synthetic_item"])
                agent._search = lambda parsed: [synthetic_item]

            def counted_suggest(item, saved_wardrobe):
                record["suggest_outfit_calls"] += 1
                return original_suggest(item, saved_wardrobe)

            agent.suggest_outfit = counted_suggest

            if use_trace:
                trace_module.start_trace()

            try:
                record["session"] = agent.run_agent(scenario["query"], wardrobe)
            finally:
                agent._search = original_search
                agent.suggest_outfit = original_suggest

            if use_trace:
                record["trace"] = trace_module.get_trace()

    except Exception as exc:  # noqa: BLE001
        record["crashed"] = f"{type(exc).__name__}: {exc}"
        record["traceback"] = traceback.format_exc()

    return record


def main():
    parser = argparse.ArgumentParser(
        description="Run deal-check scenarios and write a run log."
    )
    parser.add_argument(
        "--tries", "--trials", type=int, default=3, dest="tries",
        help="tries per scenario (default 3)",
    )
    parser.add_argument(
        "--label", default="before",
        help="run label, e.g. before or after",
    )
    args = parser.parse_args()

    problems = scenario_module.validate()
    if problems:
        print("scenarios.py has problems:\n", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        sys.exit(1)

    if not scenario_module.SCENARIOS:
        print("scenarios.py is empty.", file=sys.stderr)
        sys.exit(1)

    config.CACHE_ENABLED = False
    print("Cache is OFF for this run — that's deliberate.\n")

    rows = []
    for scenario in scenario_module.SCENARIOS:
        print(f"{scenario['name']}  ({scenario['criterion']})")

        tries = []
        for attempt in range(1, args.tries + 1):
            record = run_once(scenario)
            tries.append(record)

            if record["crashed"]:
                print(f"  try {attempt}: CRASHED — {record['crashed']}")
            elif scenario["kind"] == "tool":
                print(
                    f"  try {attempt}: "
                    f"{record['direct_result'].get('status', '(no status)')}"
                )
            else:
                session = record["session"] or {}
                if session.get("error"):
                    print(
                        f"  try {attempt}: stopped early — "
                        f"{str(session['error'])[:60]}"
                    )
                else:
                    print(
                        f"  try {attempt}: completed — "
                        f"{len(str(session.get('fit_card') or ''))} fit-card chars"
                    )
        rows.append({"scenario": scenario, "tries": tries})
        print()

    write_report(rows, args)


def write_report(rows, args):
    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    label = f"_{args.label}" if args.label else ""
    path = config.RESULTS_DIR / f"run_{stamp}{label}.md"

    n = args.tries
    headers = " | ".join(f"Try {i}" for i in range(1, n + 1))
    divider = "|".join(["---"] * n)

    lines = [
        f"# Deal Check Run Log{f' — {args.label}' if args.label else ''}",
        "",
        "- Produced by: `capstone_files/run_eval2.py::main`",
        "- Scenarios: `capstone_files/scenarios.py`",
        "- Loop: `agent.py::run_agent` · tools: `tools.py`",
        f"- Tries per scenario: {n}, caching off",
        f"- Temperature: {config.TEMPERATURE}",
        f"- When: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Paste the table below into your README. Fill in each criterion's",
        "target from `capstone_files/criteria.md`, mark each try PASS or FAIL",
        "from the output underneath, and count the passes for the Verdict.",
        "",
        f"| Criterion | Target | {headers} | Verdict |",
        f"|---|---|{divider}|---|",
    ]

    for row in rows:
        scenario = row["scenario"]
        number = scenario["criterion"]
        lines.append(
            f"| {number}. {scenario['name']} |  "
            f"| {' | '.join([' '] * n)} |  |"
        )

    lines += [
        "",
        "> Mark PASS only when the try matches the stated acceptance criterion.",
        "",
        "---",
        "",
        "## What actually happened",
        "",
    ]

    for row in rows:
        scenario = row["scenario"]
        lines += [
            f"### {scenario['name']}",
            "",
            f"- Criterion: {scenario['criterion']}",
        ]

        if scenario["kind"] == "tool":
            lines += [
                f"- Item: `{scenario['item']}`",
                f"- Maximum price: `${scenario['max_price']:.2f}`",
                "",
            ]
        else:
            lines += [
                f"- Query: `{scenario['query']}`",
                f"- Wardrobe: {scenario['wardrobe']}",
                "",
            ]

        for i, record in enumerate(row["tries"], 1):
            lines += [f"**Try {i}**", ""]

            if record["crashed"]:
                lines += [
                    "Crashed:",
                    "",
                    "```",
                    record["crashed"],
                    "```",
                    "",
                ]
                continue

            if scenario["kind"] == "tool":
                result = record["direct_result"] or {}
                lines += [
                    f"- status: `{result.get('status', '(missing)')}`",
                    f"- price: `{result.get('price')}`",
                    f"- message: {result.get('message', '(missing)')}",
                    "",
                ]
                continue

            session = record["session"] or {}
            item = session.get("selected_item") or {}
            deal_check = session.get("deal_check") or {}
            search_results = session.get("search_results") or []
            lines += [
                f"- stopped early: "
                f"{'yes — ' + str(session.get('error')) if session.get('error') else 'no'}",
                f"- selected_item: {item.get('title', '(none)')}"
                + (
                    f" (${item.get('price')}, {item.get('platform', 'synthetic')})"
                    if item
                    else ""
                ),
                f"- search_results: {len(search_results)}",
                f"- deal_check: {deal_check.get('status', '(not run)')}",
                f"- deal_check message: {deal_check.get('message', '(none)')}",
                f"- suggest_outfit calls: {record['suggest_outfit_calls']}",
                "",
            ]
            if session.get("outfit_suggestion"):
                lines += [
                    "Outfit suggestion:",
                    "",
                    "```",
                    str(session["outfit_suggestion"]),
                    "```",
                    "",
                ]
            if session.get("fit_card"):
                lines += [
                    "Fit card:",
                    "",
                    "```",
                    str(session["fit_card"]),
                    "```",
                    "",
                ]
            if record["trace"]:
                lines += ["Trace:", "", "```", record["trace"], "```", ""]

    path.write_text("\n".join(lines), encoding="utf-8")

    import generate

    print(f"Wrote {path.relative_to(config.ROOT)}")
    print(generate.usage())
    print("\nCommit this file. It is the evidence the test actually happened.")


if __name__ == "__main__":
    main()