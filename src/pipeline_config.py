# Purpose: Shared path and threshold config for all pipeline layers.
# Inputs:  Optional environment overrides (PIPELINE_DATA_PATH, PIPELINE_DELTA_PATH).
# Outputs: Path helpers imported by Bronze, Silver, Gold, and dashboard scripts.

"""Shared pipeline configuration."""

import os
from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]

AMOUNT_TOLERANCE: float = 0.01

VALID_CUSTOMER_SEGMENTS: tuple[str, ...] = ("Premium", "Standard", "Basic")
VALID_ORDER_STATUSES: tuple[str, ...] = ("Pending", "Completed", "Cancelled")


def data_input_path() -> str:
    """Return the CSV input directory (reads env var each call)."""
    return os.environ.get("PIPELINE_DATA_PATH", str(PROJECT_ROOT / "data"))


def delta_base_path() -> str:
    """Return the Delta output base directory (reads env var each call)."""
    return os.environ.get("PIPELINE_DELTA_PATH", str(PROJECT_ROOT / "delta"))


def customers_csv() -> str:
    """Return path to customers.csv."""
    return f"{data_input_path()}/customers.csv"


def orders_csv() -> str:
    """Return path to orders.csv."""
    return f"{data_input_path()}/orders.csv"


def products_csv() -> str:
    """Return path to products.csv."""
    return f"{data_input_path()}/products.csv"


def high_value_revenue_threshold() -> float:
    """Return the High-Value customer revenue threshold."""
    return float(os.environ.get("HIGH_VALUE_THRESHOLD", "5000"))


def bronze_path(table: str) -> str:
    """Return Delta path for a Bronze table."""
    return f"{delta_base_path()}/bronze_{table}"


def silver_path(table: str) -> str:
    """Return Delta path for a Silver table."""
    return f"{delta_base_path()}/silver_{table}"


def gold_path(table: str) -> str:
    """Return Delta path for a Gold table."""
    return f"{delta_base_path()}/gold_{table}"
