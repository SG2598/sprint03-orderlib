# Sprint 03 — Order Domain Library (orderlib)

A tiny domain library for consistent order total calculations (subtotal, discounts, tax, grand total).

## Public API

- `Order.add_item(sku, qty)`
- `Order.remove_item(sku)`
- `Order.subtotal()`
- `Order.discount_amount()`
- `Order.tax_amount()`
- `Order.total()`
- `Order.checkout()` (logs order_id and totals)

## Catalog

Place the provided catalog at: `data/product_catalog.json`

The loader supports common JSON shapes:
- List of products: `[{"sku": "SKU1", "name": "X", "price": 10.0}, ...]`
- Dict of products keyed by SKU: `{"SKU1": {"sku": "SKU1", "name": "X", "price": 10.0}, ...}`
- Dict with `products` key containing a list

## Discounts

- `SAVE10` → 10% off subtotal
- `SAVE20` → 20% off subtotal

Discount applies **before** tax.

## Install (editable)

```bash
pip install -e .
```

## Run tests

```bash
pytest -q
```

## Quality gates

```bash
black --check .
ruff check .
```
