# Purpose: Shared path and threshold config for all pipeline layers.
# Inputs:  Optional environment overrides (PIPELINE_DATA_PATH, PIPELINE_DELTA_PATH).
# Outputs: Path constants imported by Bronze, Silver, Gold, and dashboard scripts.

"""Shared pipeline configuration."""

import os
from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]

DATA_INPUT_PATH: str = os.environ.get("PIPELINE_DATA_PATH", str(PROJECT_ROOT / "data"))
DELTA_BASE_PATH: str = os.environ.get("PIPELINE_DELTA_PATH", str(PROJECT_ROOT / "delta"))

CUSTOMERS_CSV: str = f"{DATA_INPUT_PATH}/customers.csv"
ORDERS_CSV: str = f"{DATA_INPUT_PATH}/orders.csv"
PRODUCTS_CSV: str = f"{DATA_INPUT_PATH}/products.csv"

HIGH_VALUE_REVENUE_THRESHOLD: float = float(
    os.environ.get("HIGH_VALUE_THRESHOLD", "5000")
)
AMOUNT_TOLERANCE: float = 0.01

VALID_CUSTOMER_SEGMENTS: tuple[str, ...] = ("Premium", "Standard", "Basic")
VALID_ORDER_STATUSES: tuple[str, ...] = ("Pending", "Completed", "Cancelled")


def bronze_path(table: str) -> str:
    """Return Delta path for a Bronze table."""
    return f"{DELTA_BASE_PATH}/bronze_{table}"


def silver_path(table: str) -> str:
    """Return Delta path for a Silver table."""
    return f"{DELTA_BASE_PATH}/silver_{table}"


def gold_path(table: str) -> str:
    """Return Delta path for a Gold table."""
    return f"{DELTA_BASE_PATH}/gold_{table}"
