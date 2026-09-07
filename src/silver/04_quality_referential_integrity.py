# Purpose: Silver referential integrity — flag orphan FKs on orders; never delete rows.
# Inputs:  Orders DataFrame plus customer/product ID sets from Silver tables.
# Outputs: Orders DataFrame with RI failures appended to quality_check_result.

"""Silver referential integrity checks."""

from pyspark.sql import Column, DataFrame
from pyspark.sql.functions import col

from silver.quality_utils import append_failure, pass_rate


def apply_referential_integrity_orders(
    orders_df: DataFrame,
    customers_df: DataFrame,
    products_df: DataFrame,
) -> tuple[DataFrame, float]:
    """Flag orders whose customer_id or product_id is not in parent tables.

    Args:
        orders_df: Orders DataFrame with quality_check_result initialized.
        customers_df: Silver customers (all rows retained).
        products_df: Silver products (all rows retained).

    Returns:
        Tuple of (updated orders DataFrame, RI pass rate %).
    """
    valid_customer_ids = customers_df.select(
        col("customer_id").cast("long").alias("customer_id")
    ).distinct()
    valid_product_ids = products_df.select(
        col("product_id").cast("long").alias("product_id")
    ).distinct()

    orders = orders_df.withColumn("_cid", col("customer_id").cast("long"))
    orders = orders.withColumn("_pid", col("product_id").cast("long"))

    orders = orders.join(
        valid_customer_ids.withColumnRenamed("customer_id", "_valid_cid"),
        orders["_cid"] == col("_valid_cid"),
        "left",
    )
    orders = orders.join(
        valid_product_ids.withColumnRenamed("product_id", "_valid_pid"),
        orders["_pid"] == col("_valid_pid"),
        "left",
    )

    orphan_customer: Column = (
        col("customer_id").isNotNull() & col("_valid_cid").isNull()
    )
    orphan_product: Column = col("product_id").isNotNull() & col("_valid_pid").isNull()
    fail_condition = orphan_customer | orphan_product

    orders = append_failure(orders, orphan_customer, "customer_id not in customers")
    orders = append_failure(orders, orphan_product, "product_id not in products")

    rate = pass_rate(orders, fail_condition)
    orders = orders.drop("_cid", "_pid", "_valid_cid", "_valid_pid")
    return orders, rate
