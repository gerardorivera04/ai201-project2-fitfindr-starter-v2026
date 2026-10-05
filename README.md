# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->



---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:**  A search tool that opens up a selection of clothing listings available to pick from using a description, a optional size, and a optional max price.
- **Inputs:** description (str), size (str), max_price (float)
- **Returns:** A list of matching listing dicts, each with id, title, description, size, and price filters.
- **When it has nothing:** An empty list when no listings match the description, size, and price filters. 

### `suggest_outfit`

- **What it does:** A suggestion tool for recommending one or two outfits that combine a selected listing with the user's wardrobe.
- **Inputs:** new_item (dict listing), wardrobe (dict with an items list of wardrobe-item dicts)
- **Returns:** A non-empty string containing one or two outfit suggestions, using specifc wardrobe pieces when they are available.
- **When it has nothing:** A non-empty string with general styling advice when the wardrobe's items list is empty.

### `create_fit_card`

- **What it does:** A creation tool for providing a social-media-style caption for the selected item and the suggested outfit.
- **Inputs:** outfit (str), new-item (dict listing)
- **Returns:** A short, descriptive caption that mentions the item, the price, the platform, and the outfit's overall vibe.
- **When it has nothing:** A descriptive message when the outfit is empty or contains only whitespace.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If search_listings returns an empty list, put a message in session["error"] describing what the user could change and stop before calling suggest_outfit. Otherwise, take the first result, store it in session["selected_item"], and go to suggest_outfit.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** <!-- regex, string splitting, or asking the model — say which --> The query is parsed with regular expressions. The parser extracts a description, an optional size, and an optional max_price float.

**What moves through the session:** <!-- which fields, in what order --> The session stores the original query, then parsed description/size/max_price values, search_results, the first result as selected_item, the wardrobe, the outfit_suggestion, and finally the fit_card. If no listings are found, the error is populated and the loop stops before suggest_outfit.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```

python3 app.py ask 'denim jacket under $50'

[1] parse_query
      in:  denim jacket under $50
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 7 items: Denim Jacket — Light Wash, Cropped, 90s Track Jacket — Navy/White Stripe, High-Waisted Denim Shorts — Cutoff … +4 more
      →    7 match(es)
[3] select_item
      out: Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
[4] suggest_outfit
      in:  Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
      out: Here are two complete outfits featuring the new light-wash cropped Wrangler denim jacket, using only items fro…
      →    10 wardrobe item(s)
[5] create_fit_card
      in:  Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
      out: Scored this vintage cropped Wrangler denim jacket on poshmark for $42.00 and I'm obsessed with how it looks st…

  Found:    Denim Jacket — Light Wash, Cropped — $42.0 on poshmark

  Outfit:   Here are two complete outfits featuring the new light-wash cropped Wrangler denim jacket, using only items from your existing wardrobe:

### Outfit 1: The Double Denim Streetwear Look
*   **Top:** White ribbed tank top (`w_003`)
*   **Outerwear:** Denim Jacket — Light Wash, Cropped (`lst_007`)
*   **Bottoms:** Baggy straight-leg jeans, dark wash (`w_001`)
*   **Shoes:** Chunky white sneakers (`w_007`)
*   **Accessories:** Black crossbody bag (`w_010`)

**Why it works:** 
This look plays on the high-contrast "double denim" trend by pairing the new light wash jacket with your dark wash, high-waisted baggy jeans. Because the jeans sit high and the jacket is cropped, it creates a balanced, flattering proportion that accentuates the waist. Layering the fitted white ribbed tank underneath breaks up the heavy denim, whilethe chunky white sneakers and black crossbody bag lean into an effortless streetwear aesthetic.

***

### Outfit 2: Casual Earth-Tone Contrast
*   **Top:** Oversized grey crewneck sweatshirt (`w_004`)
*   **Outerwear:** Denim Jacket — Light Wash, Cropped (`lst_007`)
*   **Bottoms:** Wide-leg khaki trousers (`w_002`)
*   **Shoes:** Black combat boots (`w_008`)
*   **Accessories:** Brown leather belt (`w_009`)

**Why it works:**
This outfit leans into relaxed textures and smart-casual layering. Tucking the oversized grey crewneck into the wide-leg khaki trousers (pulled together by the brown leather belt) creates a neat foundation. Throwing the cropped light-wash denim jacket over the bulky grey sweatshirt adds a cool structural contrast—the shorter jacket defines the top half over the draped sweatshirt and trousers. Grounding the outfit with black combat boots adds a touch of edge that balances out the softer khaki and grey tones.

  Fit card: Scored this vintage cropped Wrangler denim jacket on poshmark for $42.00 and I'm obsessed with how it looks styled for a casual streetwear vibe. Paired it with dark-wash baggy jeans and a white tank for the ultimate effortless double-denim fit.

2 model calls this session, 1683 prompt + 492 output tokens
```

**The three tools, tested one at a time**

```
$ /usr/local/bin/python3 -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
Output: 6 matching listings were returned, all priced at or below $30.00.

$ /usr/local/bin/python3 -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, get_empty_wardrobe, load_listings; item = load_listings()[0]; populated = suggest_outfit(item, get_example_wardrobe()); empty = suggest_outfit(item, get_empty_wardrobe()); print('populated=' + ' '.join(populated.split()) + ' | empty=' + ' '.join(empty.split()))"
Output: populated=Here are two complete outfits featuring the Vintage Levi's 501 Jeans — Medium Wash, naming wardrobe pieces such as the white ribbed tank top and chunky white sneakers. | empty=Here are two ways to style these classic vintage Levi's 501 jeans, with general advice and no claim that the user owns specific pieces.

$ /usr/local/bin/python3 -c "from tools import create_fit_card; from utils.data_loader import load_listings; result = create_fit_card('jeans and white sneakers', load_listings()[0]); print(' '.join(result.split()))"
Output: Found my holy grail medium wash vintage Levi's 501 jeans on depop for just $38.00 and I am never taking them off. Paired them with crisp white sneakers for that effortlessly cool, casual streetwear vibe.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
