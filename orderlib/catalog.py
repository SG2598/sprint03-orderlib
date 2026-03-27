"""Catalog loading utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from .models import Product

DEFAULT_CATALOG_PATH = Path("data/product_catalog.json")


def load_catalog(path: Path = DEFAULT_CATALOG_PATH) -> Dict[str, Product]:
    """Load products from a catalog JSON file.

    The loader is tolerant to common shapes:
    - A list of product objects
    - A dict mapping SKU -> product object
    - A dict containing a key like "products" that holds a list

    Each product object must contain at least: sku, name, price.

    Args:
        path: Path to product_catalog.json.

    Returns:
        Mapping of sku -> Product.

    Raises:
        OSError: If file cannot be read.
        ValueError: If JSON is invalid or missing required fields.
    """

    raw = json.loads(path.read_text(encoding="utf-8"))
    items: Iterable[Mapping[str, Any]]

    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict):
        if "products" in raw and isinstance(raw["products"], list):
            items = raw["products"]
        else:
            # assume sku -> object
            items = raw.values()
    else:
        raise ValueError("Unsupported catalog JSON format")

    catalog: Dict[str, Product] = {}
    for obj in items:
        sku = str(obj.get("sku", "")).strip()
        name = str(obj.get("name", "")).strip()
        if sku == "" or name == "":
            raise ValueError("Catalog product missing sku or name")
        price_raw = obj.get("price")
        try:
            price = float(price_raw)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid price for sku {sku}") from None
        if price < 0:
            raise ValueError(f"Negative price for sku {sku}")
        catalog[sku] = Product(sku=sku, name=name, price=price)

    return catalog
