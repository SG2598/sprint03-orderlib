"""Custom exceptions for the order domain."""


class OrderLibError(Exception):
    """Base exception for orderlib."""


class UnknownDiscountError(OrderLibError):
    """Raised when an unsupported discount code is provided."""


class InvalidQuantityError(OrderLibError):
    """Raised when quantity is less than 1."""
