# Purpose: Generate sample e-commerce CSVs (customers, orders, products), then inject
#          known data-quality issues for Silver-layer testing.
# Inputs:  Config constants below (counts, seed, output directory, date bounds). No CLI args.
# Outputs: ./data/customers.csv, ./data/orders.csv, ./data/products.csv plus a printed
#          row-count and issue-injection summary.

"""Generate dirty e-commerce CSVs for the medallion pipeline (see header above)."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from faker import Faker
from numpy.random import Generator

# --- Config (no hardcoded absolute paths) ---
RANDOM_SEED: int = 42
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
DATA_DIR: Path = PROJECT_ROOT / "data"

N_CUSTOMERS: int = 10_000
N_ORDERS: int = 100_000
N_PRODUCTS: int = 500

SIGNUP_START: date = date(2020, 1, 1)

SEGMENT_VALUES: tuple[str, ...] = ("Premium", "Standard", "Basic")
SEGMENT_WEIGHTS: tuple[float, ...] = (0.20, 0.50, 0.30)

STATUS_VALUES: tuple[str, ...] = ("Pending", "Completed", "Cancelled")
STATUS_WEIGHTS: tuple[float, ...] = (0.15, 0.75, 0.10)

PRODUCT_CATEGORIES: tuple[str, ...] = (
    "Electronics",
    "Clothing",
    "Home",
    "Sports",
    "Beauty",
    "Grocery",
    "Toys",
    "Books",
)

N_NULL_EMAIL: int = 50
N_DUP_CUSTOMER_ID: int = 10
N_NULL_ORDER_CUSTOMER_ID: int = 100
N_NULL_ORDER_PRODUCT_ID: int = 200
N_ORPHAN_CUSTOMER_ID: int = 50
N_ORPHAN_PRODUCT_ID: int = 30
N_DUP_ORDER_ID: int = 20

ORPHAN_CUSTOMER_ID_BASE: int = 1_000_000
ORPHAN_PRODUCT_ID_BASE: int = 1_000_000


def _days_between(start: date, end: date) -> int:
    """Return inclusive day span from start to end (non-negative)."""
    return max((end - start).days, 0)


def generate_products(fake: Faker, rng: Generator, n: int = N_PRODUCTS) -> pd.DataFrame:
    """Build a clean products DataFrame with sequential product_id PKs.

    Args:
        fake: Seeded Faker instance for names.
        rng: Seeded NumPy generator for numeric fields.
        n: Number of product rows.

    Returns:
        DataFrame with the products.csv schema.
    """
    prices = np.round(rng.uniform(5.0, 500.0, size=n), 2)
    cost_ratios = rng.uniform(0.30, 0.85, size=n)
    costs = np.round(prices * cost_ratios, 2)
    costs = np.minimum(costs, np.round(prices - 0.01, 2))

    rows: list[dict[str, Any]] = []
    for i in range(n):
        product_id = i + 1
        category = str(rng.choice(PRODUCT_CATEGORIES))
        product_name = f"{fake.word().title()} {category} {product_id}"
        rows.append(
            {
                "product_id": product_id,
                "product_name": product_name,
                "category": category,
                "price": float(prices[i]),
                "cost": float(costs[i]),
                "stock_quantity": int(rng.integers(0, 5001)),
                "reorder_level": int(rng.integers(5, 201)),
            }
        )
    return pd.DataFrame(rows)


def generate_customers(fake: Faker, rng: Generator, n: int = N_CUSTOMERS) -> pd.DataFrame:
    """Build a clean customers DataFrame with sequential customer_id PKs.

    Args:
        fake: Seeded Faker instance for names, emails, and countries.
        rng: Seeded NumPy generator for dates, segments, and LTV.
        n: Number of customer rows.

    Returns:
        DataFrame with the customers.csv schema.
    """
    today = date.today()
    span = _days_between(SIGNUP_START, today)
    offsets = rng.integers(0, span + 1, size=n)
    segments = rng.choice(SEGMENT_VALUES, size=n, p=SEGMENT_WEIGHTS)

    ltv_low = np.where(segments == "Premium", 2000.0, np.where(segments == "Standard", 200.0, 0.0))
    ltv_high = np.where(segments == "Premium", 20000.0, np.where(segments == "Standard", 3000.0, 800.0))
    lifetime_value = np.round(rng.uniform(ltv_low, ltv_high), 2)

    rows: list[dict[str, Any]] = []
    for i in range(n):
        customer_id = i + 1
        local, domain = fake.email().split("@", 1)
        rows.append(
            {
                "customer_id": customer_id,
                "customer_name": fake.name(),
                "email": f"{local}.{customer_id}@{domain}",
                "country": fake.country(),
                "signup_date": SIGNUP_START + timedelta(days=int(offsets[i])),
                "customer_segment": str(segments[i]),
                "lifetime_value": float(lifetime_value[i]),
            }
        )
    df = pd.DataFrame(rows)
    df["signup_date"] = pd.to_datetime(df["signup_date"]).dt.date
    return df


def generate_orders(
    customers: pd.DataFrame,
    products: pd.DataFrame,
    rng: Generator,
    n: int = N_ORDERS,
) -> pd.DataFrame:
    """Build a clean orders DataFrame with valid FKs, dates, and amounts.

    Args:
        customers: Clean customers (used for FK and signup_date lower bound).
        products: Clean products (used for FK and unit_price).
        rng: Seeded NumPy generator.
        n: Number of order rows.

    Returns:
        DataFrame with the orders.csv schema.
    """
    today = date.today()
    today_ts = np.datetime64(today)

    signup_arr = np.array(customers["signup_date"].tolist(), dtype="datetime64[D]")
    price_arr = products["price"].to_numpy(dtype=float)

    customer_ids = rng.integers(1, len(customers) + 1, size=n, dtype=np.int64)
    product_ids = rng.integers(1, len(products) + 1, size=n, dtype=np.int64)
    quantities = rng.integers(1, 11, size=n, dtype=np.int64)

    signups = signup_arr[customer_ids - 1]
    spans = (today_ts - signups).astype("timedelta64[D]").astype(np.int64)
    spans = np.maximum(spans, 0)
    order_offsets = rng.integers(0, np.iinfo(np.int32).max, size=n) % (spans + 1)
    order_dates = signups + order_offsets.astype("timedelta64[D]")

    unit_prices = np.round(price_arr[product_ids - 1], 2)
    total_amounts = np.round(quantities * unit_prices, 2)
    statuses = rng.choice(STATUS_VALUES, size=n, p=STATUS_WEIGHTS)

    remaining = (today_ts - order_dates).astype("timedelta64[D]").astype(np.int64)
    remaining = np.maximum(remaining, 0)
    pay_offsets = rng.integers(0, np.iinfo(np.int32).max, size=n) % (remaining + 1)
    payment_dates = order_dates + pay_offsets.astype("timedelta64[D]")

    order_ts = pd.to_datetime(pd.Series(order_dates))
    pay_ts = pd.to_datetime(pd.Series(payment_dates))
    payment_series = pay_ts.where(pd.Series(statuses) == "Completed")

    df = pd.DataFrame(
        {
            "order_id": np.arange(1, n + 1, dtype=np.int64),
            "customer_id": customer_ids,
            "order_date": order_ts.dt.date,
            "product_id": product_ids,
            "quantity": quantities,
            "unit_price": unit_prices,
            "total_amount": total_amounts,
            "order_status": statuses,
            "payment_date": payment_series.dt.date,
        }
    )
    return df


def inject_quality_issues(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
    rng: Generator,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    """Return copies of the inputs with known quality issues injected.

    Row picks are disjoint per issue type so Silver tests can assert exact counts.
    Duplicate PKs are appended as extra rows; existing rows are not overwritten.

    Args:
        customers: Clean customers DataFrame.
        orders: Clean orders DataFrame.
        rng: Seeded NumPy generator (RANDOM_SEED).

    Returns:
        Tuple of (dirty customers, dirty orders, issue-count breakdown).
    """
    customers_out = customers.copy()
    orders_out = orders.copy()
    customers_out["email"] = customers_out["email"].astype("string")
    customers_out["customer_id"] = customers_out["customer_id"].astype("Int64")
    orders_out["customer_id"] = orders_out["customer_id"].astype("Int64")
    orders_out["product_id"] = orders_out["product_id"].astype("Int64")
    orders_out["order_id"] = orders_out["order_id"].astype("Int64")

    cust_idx = rng.choice(len(customers_out), size=N_NULL_EMAIL + N_DUP_CUSTOMER_ID, replace=False)
    null_email_idx = cust_idx[:N_NULL_EMAIL]
    dup_cust_src_idx = cust_idx[N_NULL_EMAIL : N_NULL_EMAIL + N_DUP_CUSTOMER_ID]
    customers_out.loc[null_email_idx, "email"] = pd.NA
    dup_customers = customers_out.iloc[list(dup_cust_src_idx)].copy()
    customers_out = pd.concat([customers_out, dup_customers], ignore_index=True)

    needed = (
        N_NULL_ORDER_CUSTOMER_ID
        + N_NULL_ORDER_PRODUCT_ID
        + N_ORPHAN_CUSTOMER_ID
        + N_ORPHAN_PRODUCT_ID
        + N_DUP_ORDER_ID
    )
    order_idx = rng.choice(len(orders_out), size=needed, replace=False)
    i = 0
    null_cid_idx = order_idx[i : i + N_NULL_ORDER_CUSTOMER_ID]
    i += N_NULL_ORDER_CUSTOMER_ID
    null_pid_idx = order_idx[i : i + N_NULL_ORDER_PRODUCT_ID]
    i += N_NULL_ORDER_PRODUCT_ID
    orphan_cid_idx = order_idx[i : i + N_ORPHAN_CUSTOMER_ID]
    i += N_ORPHAN_CUSTOMER_ID
    orphan_pid_idx = order_idx[i : i + N_ORPHAN_PRODUCT_ID]
    i += N_ORPHAN_PRODUCT_ID
    dup_order_src_idx = order_idx[i : i + N_DUP_ORDER_ID]

    orders_out.loc[null_cid_idx, "customer_id"] = pd.NA
    orders_out.loc[null_pid_idx, "product_id"] = pd.NA
    orders_out.loc[orphan_cid_idx, "customer_id"] = [
        ORPHAN_CUSTOMER_ID_BASE + k for k in range(N_ORPHAN_CUSTOMER_ID)
    ]
    orders_out.loc[orphan_pid_idx, "product_id"] = [
        ORPHAN_PRODUCT_ID_BASE + k for k in range(N_ORPHAN_PRODUCT_ID)
    ]
    dup_orders = orders_out.iloc[list(dup_order_src_idx)].copy()
    orders_out = pd.concat([orders_out, dup_orders], ignore_index=True)

    issue_counts: dict[str, int] = {
        "customers_null_email": N_NULL_EMAIL,
        "customers_duplicate_id_extra_rows": N_DUP_CUSTOMER_ID,
        "orders_null_customer_id": N_NULL_ORDER_CUSTOMER_ID,
        "orders_null_product_id": N_NULL_ORDER_PRODUCT_ID,
        "orders_orphan_customer_id": N_ORPHAN_CUSTOMER_ID,
        "orders_orphan_product_id": N_ORPHAN_PRODUCT_ID,
        "orders_duplicate_id_extra_rows": N_DUP_ORDER_ID,
    }
    return customers_out, orders_out, issue_counts


def write_csvs(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
    products: pd.DataFrame,
    data_dir: Path = DATA_DIR,
) -> None:
    """Write the three pipeline source CSVs under data_dir.

    Args:
        customers: Customers to persist (typically post-injection).
        orders: Orders to persist (typically post-injection).
        products: Products to persist.
        data_dir: Output directory (config DATA_DIR by default).
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    customers.to_csv(data_dir / "customers.csv", index=False, date_format="%Y-%m-%d")
    orders.to_csv(data_dir / "orders.csv", index=False, date_format="%Y-%m-%d")
    products.to_csv(data_dir / "products.csv", index=False, date_format="%Y-%m-%d")


def print_summary(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
    products: pd.DataFrame,
    issue_counts: dict[str, int],
) -> None:
    """Print generated row counts and the intentional issue breakdown.

    Args:
        customers: Final customers DataFrame.
        orders: Final orders DataFrame.
        products: Final products DataFrame.
        issue_counts: Counts from inject_quality_issues().
    """
    print("=== Generation summary ===")
    print(f"customers.csv rows: {len(customers)} (clean {N_CUSTOMERS} + {N_DUP_CUSTOMER_ID} extra dupes)")
    print(f"orders.csv rows:    {len(orders)} (clean {N_ORDERS} + {N_DUP_ORDER_ID} extra dupes)")
    print(f"products.csv rows:  {len(products)}")
    print(f"random seed:        {RANDOM_SEED}")
    print("=== Intentional quality issues ===")
    for name, count in issue_counts.items():
        print(f"  {name}: {count}")
    print(
        "  uniqueness note: extra duplicate-id rows mean "
        f"{N_DUP_CUSTOMER_ID * 2} customer rows and {N_DUP_ORDER_ID * 2} order rows share a duplicated PK"
    )


def main() -> None:
    """Generate clean data, inject issues on copies, write CSVs, print summary."""
    rng = np.random.default_rng(RANDOM_SEED)
    fake = Faker()
    Faker.seed(RANDOM_SEED)

    products = generate_products(fake, rng)
    customers_clean = generate_customers(fake, rng)
    orders_clean = generate_orders(customers_clean, products, rng)

    customers, orders, issue_counts = inject_quality_issues(customers_clean, orders_clean, rng)
    write_csvs(customers, orders, products)
    print_summary(customers, orders, products, issue_counts)


if __name__ == "__main__":
    main()
