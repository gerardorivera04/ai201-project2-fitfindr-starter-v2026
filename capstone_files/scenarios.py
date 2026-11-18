"""
Scenarios for the five FitFindr deal-check acceptance criteria.

Each scenario has a ``criterion`` from capstone_files/criteria.md. A
``tool`` scenario calls check_deal directly. A ``loop`` scenario runs
run_agent and may use a synthetic selected item for deterministic stop tests.
"""

SCENARIOS = [
    {
        "name": "in-budget price is reported",
        "criterion": 1,
        "kind": "tool",
        "item": {"title": "Denim Jacket", "price": 24.0},
        "max_price": 30.0,
        "expected_status": "within",
        "expected_message": (
            "This item costs $24.00, within your $30.00 maximum budget."
        ),
    },
    {
        "name": "near-limit price is reported",
        "criterion": 2,
        "kind": "tool",
        "item": {"title": "Denim Jacket", "price": 27.0},
        "max_price": 30.0,
        "expected_status": "near_limit",
        "expected_message": (
            "This item costs $27.00, close to your $30.00 maximum budget."
        ),
    },
    {
        "name": "over-budget item stops before outfit",
        "criterion": 3,
        "kind": "loop",
        "query": "denim jacket under $30",
        "wardrobe": "example",
        "synthetic_item": {"title": "Denim Jacket", "price": 42.0},
    },
    {
        "name": "missing price stops before outfit",
        "criterion": 4,
        "kind": "loop",
        "query": "denim jacket",
        "wardrobe": "example",
        "synthetic_item": {"title": "Denim Jacket"},
    },
    {
        "name": "missing price is unknown",
        "criterion": 4,
        "kind": "tool",
        "item": {"title": "Denim Jacket"},
        "max_price": 30.0,
        "expected_status": "unknown",
        "expected_message_fragment": "no usable price",
    },
    {
        "name": "nonnumeric price stops before outfit",
        "criterion": 4,
        "kind": "loop",
        "query": "denim jacket",
        "wardrobe": "example",
        "synthetic_item": {"title": "Denim Jacket", "price": "unknown"},
    },
    {
        "name": "nonnumeric price is unknown",
        "criterion": 4,
        "kind": "tool",
        "item": {"title": "Denim Jacket", "price": "unknown"},
        "max_price": 30.0,
        "expected_status": "unknown",
        "expected_message_fragment": "no usable price",
    },
    {
        "name": "deal remains attached to selected item",
        "criterion": 5,
        "kind": "loop",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Check scenario shape before running an evaluation."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name", "").strip():
            problems.append(f"scenario {i} has no name")
        if scenario.get("criterion") not in range(1, 6):
            problems.append(f"scenario {i} has invalid criterion")
        if scenario.get("kind") not in {"tool", "loop"}:
            problems.append(f"scenario {i} has invalid kind")
        if scenario["kind"] == "tool":
            if not isinstance(scenario.get("item"), dict):
                problems.append(f"scenario {i} has no item")
            if "max_price" not in scenario:
                problems.append(f"scenario {i} has no max_price")
        else:
            if not scenario.get("query", "").strip():
                problems.append(f"scenario {i} has no query")
            if scenario.get("wardrobe") not in WARDROBES:
                problems.append(
                    f"scenario {i} has wardrobe {scenario.get('wardrobe')!r}"
                )
    return problems