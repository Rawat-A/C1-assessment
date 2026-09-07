# Purpose: Silver business-logic validation — amounts, enums, payment rules; never delete rows.
# Inputs:  DataFrames with quality_check_result initialized.
# Outputs: DataFrame with business-logic failures appended to quality_check_result.

"""Silver business-logic quality checks."""

from pyspark.sql import Column, DataFrame
from pyspark.sql.functions import abs, col

from pipeline_config import (
    AMOUNT_TOLERANCE,
    VALID_CUSTOMER_SEGMENTS,
    VALID_ORDER_STATUSES,
)
from silver.quality_utils import append_failure, pass_rate


def apply_business_logic_customers(df: DataFrame) -> tuple[DataFrame, float]:
    """Validate customer segment enum and non-negative lifetime_value.

    Args:
        df: Customers DataFrame with quality_check_result initialized.

    Returns:
        Tuple of (updated DataFrame, business-logic pass rate %).
    """
    invalid_segment: Column = (
        col("customer_segment").isNotNull()
        & ~col("customer_segment").isin(list(VALID_CUSTOMER_SEGMENTS))
    )
    negative_ltv: Column = col("lifetime_value").isNotNull() & (col("lifetime_value") < 0)
    fail_condition = invalid_segment | negative_ltv

    df = append_failure(df, invalid_segment, "invalid customer_segment value")
    df = append_failure(df, negative_ltv, "lifetime_value is negative")
    return df, pass_rate(df, fail_condition)


def apply_business_logic_orders(df: DataFrame) -> tuple[DataFrame, float]:
    """Validate order amounts, status enum, and payment_date rules.

    Args:
        df: Orders DataFrame with quality_check_result initialized.

    Returns:
        Tuple of (updated DataFrame, business-logic pass rate %).
    """
    invalid_status: Column = (
        col("order_status").isNotNull()
        & ~col("order_status").isin(list(VALID_ORDER_STATUSES))
    )
    bad_quantity: Column = col("quantity").isNotNull() & (col("quantity") <= 0)
    negative_unit: Column = col("unit_price").isNotNull() & (col("unit_price") < 0)
    negative_total: Column = col("total_amount").isNotNull() & (col("total_amount") < 0)
    amount_mismatch: Column = (
        col("quantity").isNotNull()
        & col("unit_price").isNotNull()
        & col("total_amount").isNotNull()
        & (
            abs(col("total_amount") - (col("quantity") * col("unit_price")))
            > AMOUNT_TOLERANCE
        )
    )
    completed_no_payment: Column = (
        (col("order_status") == "Completed") & col("payment_date").isNull()
    )

    checks: list[tuple[Column, str]] = [
        (invalid_status, "invalid order_status value"),
        (bad_quantity, "quantity must be greater than zero"),
        (negative_unit, "unit_price is negative"),
        (negative_total, "total_amount is negative"),
        (amount_mismatch, "total_amount does not equal quantity * unit_price"),
        (completed_no_payment, "Completed order missing payment_date"),
    ]
    fail_condition = checks[0][0]
    for condition, reason in checks:
        df = append_failure(df, condition, reason)
        fail_condition = fail_condition | condition
    return df, pass_rate(df, fail_condition)


def apply_business_logic_products(df: DataFrame) -> tuple[DataFrame, float]:
    """Validate product pricing and inventory business rules.

    Args:
        df: Products DataFrame with quality_check_result initialized.

    Returns:
        Tuple of (updated DataFrame, business-logic pass rate %).
    """
    negative_price: Column = col("price").isNotNull() & (col("price") < 0)
    negative_cost: Column = col("cost").isNotNull() & (col("cost") < 0)
    cost_not_less_than_price: Column = (
        col("price").isNotNull()
        & col("cost").isNotNull()
        & (col("cost") >= col("price"))
    )
    negative_stock: Column = (
        col("stock_quantity").isNotNull() & (col("stock_quantity") < 0)
    )
    negative_reorder: Column = (
        col("reorder_level").isNotNull() & (col("reorder_level") < 0)
    )

    checks: list[tuple[Column, str]] = [
        (negative_price, "price is negative"),
        (negative_cost, "cost is negative"),
        (cost_not_less_than_price, "cost must be less than price"),
        (negative_stock, "stock_quantity is negative"),
        (negative_reorder, "reorder_level is negative"),
    ]
    fail_condition = checks[0][0]
    for condition, reason in checks:
        df = append_failure(df, condition, reason)
        fail_condition = fail_condition | condition
    return df, pass_rate(df, fail_condition)
