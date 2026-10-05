"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import json
import re

import config
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

_STOPWORDS = {
    "a", "an", "and", "the", "for", "with", "under", "over", "in", "of",
}

def _keywords(text: str) -> set[str]:
    """ Lowercase words worth matching on, stopwords removed."""
    words = re.findall(r"[a-zA-Z0-9]+", (text or "").lower())
    return {w for w in words if w not in _STOPWORDS and len(w)> 1}

def _size_tokens(size: str) -> set[str]:
    cleaned = re.sub(r"\([^)]*\)", " ", size or "") # drop parentheticals
    parts = [p.strip().upper() for p in cleaned.split("/")]
    tokens = {p for p in parts if p}
    # "W30 L30" should also match a plain "W30" request
    for part in list(tokens):
        tokens.update(w for w in part.split() if re.fullmatch(r"[WL]\d+", w))
    return tokens

def _size_matches(wanted: str, listing_size: str) -> bool:
    if not wanted:
        return True
    listing_tokens = _size_tokens(listing_size)
    if any(token.startswith("ONE SIZE") for token in listing_tokens):
        return True
    return bool(_size_tokens(wanted) & listing_tokens)

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    wanted = _keywords(description)
    if not wanted:
        return []

    scored = []
    for listing in load_listings():
        if max_price is not None and listing["price"] > max_price:
            continue
        if size and not _size_matches(size, listing["size"]):
            continue

        title_words = _keywords(listing["title"])
        other_words = _keywords(" ".join([
            listing["description"],
            listing["category"],
            " ".join(listing["style_tags"]),
            " ".join(listing["colors"]),
            listing["brand"] or "",  # brand is None for most listings
        ]))
        # Title hits count double — they're the strongest signal
        score = 2 * len(wanted & title_words) + len(wanted & other_words)
        if score > 0:
            scored.append((score, listing))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for _, listing in scored[:config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    wardrobe_items = wardrobe.get("items") or []
    item_details = json.dumps(new_item, indent=2, ensure_ascii=False)

    if not wardrobe_items:
        prompt = (
            "Suggest one or two outfits for this clothing item. The user has "
            "not added any wardrobe items yet, so give general styling advice "
            "about the kinds of pieces, colors, shoes, and accessories that "
            "would work with it. Do not claim the user owns any specific piece.\n\n"
            f"Item:\n{item_details}"
        )
    else:
        wardrobe_details = json.dumps(wardrobe_items, indent=2, ensure_ascii=False)
        prompt = (
            "Suggest one or two complete outfits featuring this new clothing "
            "item. Use and name specific pieces from the user's wardrobe, and "
            "do not invent wardrobe items. Briefly explain why each combination "
            "works.\n\n"
            f"New item:\n{item_details}\n\n"
            f"User wardrobe:\n{wardrobe_details}"
        )

    return generate(prompt)


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return (
            "No fit card yet — there's no outfit suggestion to caption. "
            "Get an outfit from suggest_outfit() first, then try again."
        )

    brand = new_item.get("brand") or "unbranded"  # brand is None for most listings
    prompt = (
        "Write a 2-4 sentence caption for a social media post about this "
        "thrifted find. Make it sound like a real person posting their fit, "
        "not a product description. Mention the item, its price, and the "
        "platform it came from exactly once each, and be specific about the "
        "vibe of the outfit. Return only the caption.\n\n"
        f"Item: {new_item.get('title')}\n"
        f"Brand: {brand}\n"
        f"Price: ${new_item.get('price', 0):.2f}\n"
        f"Platform: {new_item.get('platform')}\n"
        f"Style tags: {', '.join(new_item.get('style_tags') or [])}\n"
        f"Colors: {', '.join(new_item.get('colors') or [])}\n\n"
        f"Outfit:\n{outfit.strip()}"
    )

    return generate(prompt).strip()
