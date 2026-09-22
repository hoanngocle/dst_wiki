from __future__ import annotations


def normalize_recipes(registrations: dict) -> list[dict]:
    """Return stable runtime recipes; registry keys already express final override state."""
    return sorted(registrations["recipes"].values(), key=lambda recipe: (recipe["product"], recipe["id"]))
