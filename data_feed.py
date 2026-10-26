import os
from pathlib import Path
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv



load_dotenv()

if "port" not in os.environ:
    os.environ["port"] = "5432"

# ============================================================
# CONFIGURATION
# ============================================================


DB_CONFIG = {
    "host": os.environ["host"],
    "port": int(os.environ["port"]),
    "database": os.environ["database"],
    "user": os.environ["user"],
    "password": os.environ["password"],
}

CSV_DIR = Path(__file__).resolve().parent / "data"


# ============================================================
# CREATE TABLES
# ============================================================

create_tables_sql = """
CREATE SCHEMA IF NOT EXISTS public;

CREATE TABLE IF NOT EXISTS public.customers (
    customer_id BIGINT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    area TEXT,
    pincode VARCHAR(20),
    registration_date DATE,
    customer_segment TEXT,
    total_orders INTEGER,
    avg_order_value NUMERIC(12, 2)
);

CREATE TABLE IF NOT EXISTS public.products (
    product_id BIGINT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT,
    brand TEXT,
    price NUMERIC(12, 2),
    mrp NUMERIC(12, 2),
    margin_percentage NUMERIC(7, 2),
    shelf_life_days INTEGER,
    min_stock_level INTEGER,
    max_stock_level INTEGER
);

CREATE TABLE IF NOT EXISTS public.orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES public.customers(customer_id),
    order_date TIMESTAMP,
    promised_delivery_time TIMESTAMP,
    actual_delivery_time TIMESTAMP,
    delivery_status TEXT,
    order_total NUMERIC(12, 2),
    payment_method TEXT,
    delivery_partner_id BIGINT,
    store_id BIGINT
);

CREATE TABLE IF NOT EXISTS public.order_items (
    order_id BIGINT NOT NULL REFERENCES public.orders(order_id),
    product_id BIGINT NOT NULL REFERENCES public.products(product_id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL,
    PRIMARY KEY (order_id, product_id)
);

CREATE TABLE IF NOT EXISTS public.inventory (
    product_id BIGINT NOT NULL REFERENCES public.products(product_id),
    date DATE NOT NULL,
    stock_received INTEGER,
    damaged_stock INTEGER,
    PRIMARY KEY (product_id, date)
);

-- PostgreSQL does not automatically index the referencing side of foreign keys.
CREATE INDEX IF NOT EXISTS idx_orders_customer_id
    ON public.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date
    ON public.orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_delivery_status
    ON public.orders(delivery_status);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id
    ON public.order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_date
    ON public.inventory(date);
CREATE INDEX IF NOT EXISTS idx_products_category
    ON public.products(category);
"""


def load_csv(cursor, table_name, csv_file, columns):
    """Load one CSV into its matching public table with PostgreSQL COPY."""
    file_path = CSV_DIR / csv_file
    if not file_path.is_file():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    copy_sql = sql.SQL("""
        COPY {} ({})
        FROM STDIN
        WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',', NULL '')
    """).format(
        sql.Identifier("public", table_name),
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
    )

    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        cursor.copy_expert(copy_sql, file)

    print(f"Loaded {csv_file}")


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(create_tables_sql)

                cursor.execute("SET LOCAL datestyle = 'ISO, DMY'")

                cursor.execute("""
                    TRUNCATE TABLE
                        public.order_items,
                        public.inventory,
                        public.orders,
                        public.products,
                        public.customers
                    CASCADE
                """)

                load_csv(cursor, "customers", "customers.csv", [
                    "customer_id", "customer_name", "email", "phone", "address",
                    "area", "pincode", "registration_date", "customer_segment",
                    "total_orders", "avg_order_value",
                ])
                load_csv(cursor, "products", "products.csv", [
                    "product_id", "product_name", "category", "brand", "price",
                    "mrp", "margin_percentage", "shelf_life_days",
                    "min_stock_level", "max_stock_level",
                ])
                load_csv(cursor, "orders", "orders.csv", [
                    "order_id", "customer_id", "order_date", "promised_delivery_time",
                    "actual_delivery_time", "delivery_status", "order_total",
                    "payment_method", "delivery_partner_id", "store_id",
                ])
                load_csv(cursor, "order_items", "order_items.csv", [
                    "order_id", "product_id", "quantity", "unit_price",
                ])
                load_csv(cursor, "inventory", "inventory.csv", [
                    "product_id", "date", "stock_received", "damaged_stock",
                ])

                print("\nRecord counts:")
                for table in ("customers", "products", "orders", "order_items", "inventory"):
                    cursor.execute(
                        sql.SQL("SELECT COUNT(*) FROM public.{}").format(
                            sql.Identifier(table)
                        )
                    )
                    print(f"{table:<15} {cursor.fetchone()[0]:>10,}")

        print("\nData loaded successfully and transaction committed.")
    finally:
        conn.close()
        print("PostgreSQL connection closed.")


if __name__ == "__main__":
    main()
