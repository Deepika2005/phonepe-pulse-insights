import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("mysql+mysqlconnector://root:Deepika93@localhost/phonepe_pulse")

# ── 1. Top 10 states by total transaction amount ─────────────────────
q1 = pd.read_sql("""
    SELECT state, SUM(amount) AS total_amount, SUM(count) AS total_count
    FROM aggregated_transaction
    GROUP BY state
    ORDER BY total_amount DESC
    LIMIT 10
""", engine)
print("\n1. Top 10 States by Transaction Amount:")
print(q1.to_string(index=False))

# ── 2. Most popular payment category ─────────────────────────────────
q2 = pd.read_sql("""
    SELECT name, SUM(count) AS total_count, SUM(amount) AS total_amount
    FROM aggregated_transaction
    GROUP BY name
    ORDER BY total_count DESC
""", engine)
print("\n2. Most Popular Payment Categories:")
print(q2.to_string(index=False))

# ── 3. Year-wise transaction growth ──────────────────────────────────
q3 = pd.read_sql("""
    SELECT year, SUM(count) AS total_transactions, SUM(amount) AS total_amount
    FROM aggregated_transaction
    GROUP BY year
    ORDER BY year
""", engine)
print("\n3. Year-wise Transaction Growth:")
print(q3.to_string(index=False))

# ── 4. Top 10 districts by transaction amount ─────────────────────────
q4 = pd.read_sql("""
    SELECT state, district, SUM(amount) AS total_amount
    FROM map_transaction
    GROUP BY state, district
    ORDER BY total_amount DESC
    LIMIT 10
""", engine)
print("\n4. Top 10 Districts by Transaction Amount:")
print(q4.to_string(index=False))

# ── 5. Top mobile brands used ────────────────────────────────────────
q5 = pd.read_sql("""
    SELECT brand, SUM(count) AS total_users
    FROM aggregated_user
    GROUP BY brand
    ORDER BY total_users DESC
    LIMIT 10
""", engine)
print("\n5. Top Mobile Brands:")
print(q5.to_string(index=False))

# ── 6. Top 10 states by registered users ─────────────────────────────
q6 = pd.read_sql("""
    SELECT state, SUM(registered_users) AS total_users
    FROM map_user
    GROUP BY state
    ORDER BY total_users DESC
    LIMIT 10
""", engine)
print("\n6. Top 10 States by Registered Users:")
print(q6.to_string(index=False))

# ── 7. Quarterly trend ────────────────────────────────────────────────
q7 = pd.read_sql("""
    SELECT year, quarter, SUM(count) AS total_transactions
    FROM aggregated_transaction
    GROUP BY year, quarter
    ORDER BY year, quarter
""", engine)
print("\n7. Quarterly Transaction Trend:")
print(q7.to_string(index=False))

print("\nAll queries ran successfully! ✅")