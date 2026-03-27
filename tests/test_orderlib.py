from __future__ import annotations

import json
from pathlib import Path

import pytest

from orderlib import InvalidQuantityError, Order, UnknownDiscountError


def _write_catalog(tmp_path: Path) -> Path:
    data = [
        {"sku": "A", "name": "Apple", "price": 10.0},
        {"sku": "B", "name": "Banana", "price": 5.0},
    ]
    p = tmp_path / "product_catalog.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_subtotal_single_item(tmp_path: Path) -> None:
    catalog = _write_catalog(tmp_path)
    order = Order(tax_rate=0.0, catalog_path=catalog)
    order.add_item("A", 2)
    assert order.subtotal() == 20.0
    assert order.total() == 20.0


def test_multiple_items_and_tax(tmp_path: Path) -> None:
    catalog = _write_catalog(tmp_path)
    order = Order(tax_rate=0.10, catalog_path=catalog)
    order.add_item("A", 1)  # 10
    order.add_item("B", 2)  # 10
    assert order.subtotal() == 20.0
    assert order.discount_amount() == 0.0
    assert order.tax_amount() == 2.0
    assert order.total() == 22.0


def test_discount_applies_before_tax(tmp_path: Path) -> None:
    catalog = _write_catalog(tmp_path)
    order = Order(tax_rate=0.10, discount_code="SAVE10", catalog_path=catalog)
    order.add_item("A", 2)  # subtotal 20
    assert order.subtotal() == 20.0
    assert order.discount_amount() == 2.0
    assert order.tax_amount() == 1.8  # tax on 18
    assert order.total() == 19.8


def test_discount_save20(tmp_path: Path) -> None:
    catalog = _write_catalog(tmp_path)
    order = Order(tax_rate=0.0, discount_code="SAVE20", catalog_path=catalog)
    order.add_item("B", 3)  # subtotal 15
    assert order.discount_amount() == 3.0
    assert order.total() == 12.0


def test_unknown_discount_raises(tmp_path: Path) -> None:
    catalog = _write_catalog(tmp_path)
    with pytest.raises(UnknownDiscountError):
        Order(tax_rate=0.0, discount_code="SAVE50", catalog_path=catalog)


def test_invalid_quantity_raises(tmp_path: Path) -> None:
    catalog = _write_catalog(tmp_path)
    order = Order(tax_rate=0.0, catalog_path=catalog)
    with pytest.raises(InvalidQuantityError):
        order.add_item("A", 0)


def test_remove_item(tmp_path: Path) -> None:
    catalog = _write_catalog(tmp_path)
    order = Order(tax_rate=0.0, catalog_path=catalog)
    order.add_item("A", 1)
    order.remove_item("A")
    assert order.subtotal() == 0.0
    with pytest.raises(KeyError):
        order.remove_item("A")
