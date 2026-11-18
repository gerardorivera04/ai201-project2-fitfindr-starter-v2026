# Acceptance criteria — FitFindr's Deal Check

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. The deal check reports an in-budget listing

Calling `check_deal({"title": "Denim Jacket", "price": 24.0}, 30.0)` returns
exactly `status: "within"` and the message
`"This item costs $24.00, within your $30.00 maximum budget."` — in 5 of 5
tries.

**Why this target:** A 30-dollar budget is an exact, well-known example in the
existing FitFindr data. This target is stricter than a sample response only
with a human-readable amount because the status must feed the planning-loop
branch, while 5 of 5 is appropriate because a local price comparison has no
model variability.

---

## 2. The deal check identifies a near-limit price

Calling `check_deal({"title": "Denim Jacket", "price": 27.0}, 30.0)` returns
exactly `status: "near_limit"` and the message
`"This item costs $27.00, close to your $30.00 maximum budget."` — in 5 of 5
tries.

**Why this target:** The 90% threshold is 27 dollars on a 30-dollar budget, so
this example is a direct boundary test. 5 of 5 is not looser than necessary
because a three-dollar gap is small enough that misclassifying the deal as
ordinary “within” would hide useful warning context. The threshold is not
stricter than 90% because 27 dollars is already explicitly near 30 dollars
and a fully exact 100% cap would miss the intended warning.

---

## 3. An over-budget item stops before outfit suggestion

Run `run_agent("denim jacket under $30", wardrobe)` five times, and make the
search result used by the loop cost $42.00. For each run, the loop sets
`deal_check.status` to `over_budget`, puts the budget error in `session["error"]`,
and never calls `suggest_outfit` — in 5 of 5 tries.

**Why this target:** Recommending an outfit for an item outside the user's
stated ceiling would spend effort on a purchase the user cannot afford. 5 of 5
is required because this is a deterministic bad path, while testing 42 dollars
against 30 dollars avoids an ambiguous boundary close to the 90% threshold.

---

## 4. A listing with no usable price stops safely

Run `check_deal({"title": "Denim Jacket"}, 30.0)` and
`check_deal({"title": "Denim Jacket", "price": "unknown"}, 30.0)` separately.
Each call returns `status: "unknown"` and a message containing “no usable
price.” Then run the loop with each listing selected: `session["error"]`
contains “no usable price,” and `suggest_outfit` is not called. Pass both bad
price forms on 5 separate loop tries each — 10 loop tries total.

**Why this target:** Thrift listings can omit or corrupt price fields, and
recommending the item as affordable would make an unsupported claim. 5 of 5
is stricter than treating this as a model-quality issue because price validity
is a local, deterministic check. Missing and nonnumeric prices are both
included so the test catches the same failure in the two forms the data can
contain.

---

## 5. The deal result remains attached to the selected item

Run `run_agent("vintage graphic tee under $30", example wardrobe)` five times.
For each run, record the first item returned by `search_listings`, the
`selected_item` stored in the session, and `deal_check`. Compare the three
numeric and text fields as follows: `selected_item.title` equals the first
search result's title, `selected_item.price` equals that result's price,
`deal_check.price` equals `selected_item.price`, and the item price formatted
as `"$24.00"` (or the actual selected price formatted with two decimals)
appears in `deal_check.message` — in 5 of 5 tries.

**Why this target:** This state check protects against a deal result being
computed for one listing after search has selected another. 5 of 5 is required
because state propagation in this local loop is deterministic: the first
search result is stored, then passed directly to `check_deal`. A 4 of 5 target
would permit the listing/price mismatch this extension is meant to prevent,
and no search-model variability justifies that miss.
