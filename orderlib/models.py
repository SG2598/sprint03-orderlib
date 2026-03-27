"""Dataclasses representing core domain models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Product:
    """A product from the catalog.

    Attributes:
        sku: Unique product identifier.
        name: Display name.
        price: Unit price (non-negative).
    """

    sku: str
    name: str
    price: float


@dataclass(frozen=True, slots=True)
class LineItem:
    """A line item in an order.

    Attributes:
        product: The product being purchased.
        quantity: Quantity purchased (>= 1).
    """

    product: Product
    quantity: int

    @property
    def total(self) -> float:
        """Return the total price for this line item."""

        return float(self.quantity) * float(self.product.price)
