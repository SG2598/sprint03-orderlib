"""Order aggregate and business rules (tax, discounts, totals)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional
from uuid import uuid4

from .catalog import DEFAULT_CATALOG_PATH, load_catalog
from .exceptions import InvalidQuantityError, UnknownDiscountError
from .models import LineItem, Product

_LOGGER = logging.getLogger(__name__)


_DISCOUNTS: Dict[str, float] = {
    "SAVE10": 0.10,
    "SAVE20": 0.20,
}


@dataclass(slots=True)
class Order:
    """An order containing line items and pricing rules.

    Public API:
        - add_item(sku, qty)
        - remove_item(sku)
        - subtotal(), discount_amount(), tax_amount(), total()
        - checkout()

    Discount is applied to subtotal before tax.

    Args:
        tax_rate: Tax rate as a decimal (e.g., 0.18 for 18%). Defaults to 0.0.
        discount_code: Optional discount code (SAVE10, SAVE20).
        catalog_path: Optional path to product catalog JSON.
    """

    tax_rate: float = 0.0
    discount_code: Optional[str] = None
    catalog_path: Path = DEFAULT_CATALOG_PATH
    order_id: str = field(default_factory=lambda: uuid4().hex)
    _catalog: Dict[str, Product] = field(init=False, repr=False)
    _items: Dict[str, LineItem] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        """Load catalog and validate initialization."""

        if self.tax_rate < 0:
            raise ValueError("tax_rate must be non-negative")
        self._catalog = load_catalog(self.catalog_path)
        if self.discount_code is not None:
            self._validate_discount(self.discount_code)

    def _validate_discount(self, code: str) -> None:
        """Validate discount code.

        Args:
            code: Discount code string.

        Raises:
            UnknownDiscountError: If the code is not supported.
        """

        normalized = code.strip().upper()
        if normalized not in _DISCOUNTS:
            raise UnknownDiscountError(f"Unknown discount code: {code}")

    def add_item(self, sku: str, qty: int) -> None:
        """Add an item to the order.

        If the SKU already exists, its quantity is increased.

        Args:
            sku: Product SKU.
            qty: Quantity (must be >= 1).

        Raises:
            InvalidQuantityError: If qty < 1.
            KeyError: If SKU does not exist in catalog.
        """

        if qty < 1:
            raise InvalidQuantityError("Quantity must be >= 1")

        sku_norm = sku.strip()
        if sku_norm not in self._catalog:
            raise KeyError(f"Unknown SKU: {sku}")

        if sku_norm in self._items:
            current = self._items[sku_norm]
            new_qty = current.quantity + qty
            self._items[sku_norm] = LineItem(product=current.product, quantity=new_qty)
        else:
            product = self._catalog[sku_norm]
            self._items[sku_norm] = LineItem(product=product, quantity=qty)

    def remove_item(self, sku: str) -> None:
        """Remove an item from the order.

        Args:
            sku: Product SKU.

        Raises:
            KeyError: If SKU is not present in the order.
        """

        sku_norm = sku.strip()
        if sku_norm not in self._items:
            raise KeyError(f"SKU not in order: {sku}")
        del self._items[sku_norm]

    def set_discount(self, code: Optional[str]) -> None:
        """Set or clear the discount code.

        Args:
            code: Discount code (SAVE10, SAVE20) or None to clear.

        Raises:
            UnknownDiscountError: If code is not supported.
        """

        if code is None:
            self.discount_code = None
            return
        self._validate_discount(code)
        self.discount_code = code.strip().upper()

    def items(self) -> Dict[str, LineItem]:
        """Return a shallow copy of items in the order."""

        return dict(self._items)

    def subtotal(self) -> float:
        """Compute subtotal of all line items (before discount and tax)."""

        return sum(item.total for item in self._items.values())

    def discount_amount(self) -> float:
        """Compute discount amount applied to subtotal (before tax)."""

        if not self.discount_code:
            return 0.0
        rate = _DISCOUNTS[self.discount_code.strip().upper()]
        return self.subtotal() * rate

    def taxable_amount(self) -> float:
        """Compute amount on which tax should be applied (after discount)."""

        return self.subtotal() - self.discount_amount()

    def tax_amount(self) -> float:
        """Compute tax on (subtotal - discount)."""

        return self.taxable_amount() * float(self.tax_rate)

    def total(self) -> float:
        """Compute grand total: (subtotal - discount) + tax."""

        return self.taxable_amount() + self.tax_amount()

    def checkout(self) -> float:
        """Checkout the order.

        Logs order_id and totals (no secrets) and returns the grand total.

        Returns:
            Grand total for the order.
        """

        subtotal = self.subtotal()
        discount = self.discount_amount()
        tax = self.tax_amount()
        total = self.total()

        _LOGGER.info(
            "checkout order_id=%s subtotal=%.2f discount=%.2f tax=%.2f total=%.2f",
            self.order_id,
            subtotal,
            discount,
            tax,
            total,
        )

        return total
