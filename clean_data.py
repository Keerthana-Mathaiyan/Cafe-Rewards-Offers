# =============================
# 1. IMPORTS
# =============================
import pandas as pd
import numpy as np
import mysql.connector
import ast
import json
import math
from sqlalchemy import create_engine
from mysql.connector import Error

# =============================
# 2. MYSQL CONNECTION (SQLALCHEMY FOR SAFETY)
# =============================
engine = create_engine(
    "mysql+mysqlconnector://root:12345@localhost/cafe_analytics"
)

# =============================
# 3. LOAD DATA
# =============================
customers = pd.read_csv("data/customers.csv")
offers = pd.read_csv("data/offers.csv")
events = pd.read_csv("data/events.csv")

print("CSV Loaded")

# =============================
# 4. CLEAN CUSTOMERS
# =============================
clean_customers = customers.copy()

clean_customers["became_member_on"] = pd.to_datetime(
    clean_customers["became_member_on"],
    format="%Y%m%d",
    errors="coerce"
)

clean_customers.loc[clean_customers["age"] == 118, "age"] = np.nan
clean_customers["gender"] = clean_customers["gender"].fillna("Unknown")
clean_customers["income"] = clean_customers["income"].fillna(
    clean_customers["income"].median()
)

print("Customers cleaned")

# =============================
# 5. CLEAN OFFERS
# =============================
clean_offers = offers.copy()

clean_offers["offer_type"] = clean_offers["offer_type"].str.lower().str.strip()

def parse_channels(x):
    try:
        return ast.literal_eval(x) if isinstance(x, str) else x
    except:
        return []

clean_offers["channels"] = clean_offers["channels"].apply(
    lambda x: json.dumps(parse_channels(x))
)

print("Offers cleaned")

# =============================
# 6. CLEAN EVENTS
# =============================
clean_events = events.copy()

def parse_value(x):
    try:
        return ast.literal_eval(x) if isinstance(x, str) else x
    except:
        return {}

clean_events["value"] = clean_events["value"].apply(parse_value)

clean_events["offer_id"] = clean_events["value"].apply(
    lambda x: x.get("offer id") if isinstance(x, dict) else None
)

clean_events["amount"] = clean_events["value"].apply(
    lambda x: x.get("amount") if isinstance(x, dict) else None
)

clean_events.drop(columns=["value"], inplace=True)

print("Events cleaned")

# =============================
# 7. SAFE VALUE HANDLER
# =============================
def safe_value(x):

    # handle None
    if x is None:
        return None

    # handle list/dict
    if isinstance(x, (list, dict)):
        return json.dumps(x)

    # handle NaN safely
    try:
        if isinstance(x, float) and math.isnan(x):
            return None
    except:
        pass

    # fallback pandas NaN
    try:
        if pd.isna(x):
            return None
    except:
        return x

    return x


def clean_row(row):
    return [safe_value(x) for x in row]

# =============================
# 8. BATCH INSERT FUNCTION
# =============================
def batch_insert(df, table, batch_size=1000):

    cols = ",".join(df.columns)
    placeholders = ",".join(["%s"] * len(df.columns))

    sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"

    data = df.values.tolist()

    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]

        safe_batch = [clean_row(row) for row in batch]

        with engine.raw_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(sql, safe_batch)
            conn.commit()

    print(f"{table} loaded successfully 🚀")

# =============================
# 9. CREATE TABLES
# =============================
with engine.raw_connection() as conn:
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clean_customers (
        customer_id VARCHAR(50),
        age FLOAT,
        gender VARCHAR(20),
        income FLOAT,
        became_member_on DATE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clean_offers (
        offer_id VARCHAR(50),
        offer_type VARCHAR(20),
        difficulty INT,
        reward INT,
        duration INT,
        channels TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clean_events (
        customer_id VARCHAR(50),
        event VARCHAR(50),
        time INT,
        offer_id VARCHAR(50),
        amount FLOAT
    )
    """)

    conn.commit()

print("Tables created")

# =============================
# 10. LOAD DATA INTO MYSQL
# =============================
batch_insert(clean_customers, "clean_customers")
batch_insert(clean_offers, "clean_offers")
batch_insert(clean_events, "clean_events")

print("ETL Pipeline Completed Successfully 🚀")