import os
import json
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ── Load environment variables ──────────────────────────────────────
load_dotenv()

# ── DB Connection ────────────────────────────────────────────────────
# Store credentials in .env file as:
# DATABASE_URL=mysql+mysqlconnector://root:YOUR_PASSWORD@localhost/phonepe_pulse
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://root:Deepika93@localhost/phonepe_pulse")
engine = create_engine(DATABASE_URL)

PULSE_PATH = "pulse/data"
CHUNK_SIZE = 1000  # rows per batch insert


# ── Helper: safe file loader ─────────────────────────────────────────
def load_json(filepath):
    """Safely load a JSON file. Returns None on error."""
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"  ⚠ Skipping {filepath}: {e}")
        return None


# ── Helper: save to SQL ──────────────────────────────────────────────
def save_to_sql(df, table_name, engine):
    """Replace table and load DataFrame in chunks."""
    if df.empty:
        print(f"  ⚠ No data found for {table_name}, skipping.")
        return
    df.to_sql(table_name, con=engine, if_exists="replace", index=False, chunksize=CHUNK_SIZE)
    print(f"{table_name}: {len(df)} rows loaded ✅")


# ── Helper: add indexes after load ───────────────────────────────────
def add_indexes(engine, table_name, columns):
    """Add indexes to a table for query performance."""
    with engine.connect() as conn:
        for col in columns:
            index_name = f"idx_{table_name}_{col}"
            try:
                conn.execute(text(
                    f"ALTER TABLE `{table_name}` ADD INDEX `{index_name}` (`{col}`)"
                ))
                conn.commit()
            except Exception:
                pass  # Index already exists — safe to ignore


# ════════════════════════════════════════════════════════════════════
# AGGREGATED TABLES
# ════════════════════════════════════════════════════════════════════

def load_aggregated_transaction(pulse_path, engine):
    rows = []
    path = os.path.join(pulse_path, "aggregated", "transaction", "country", "india", "state")
    for state in os.listdir(path):
        for year in os.listdir(os.path.join(path, state)):
            for file in os.listdir(os.path.join(path, state, year)):
                data = load_json(os.path.join(path, state, year, file))
                if not data:
                    continue
                for item in data["data"].get("transactionData") or []:
                    rows.append({
                        "state":   state,
                        "year":    int(year),
                        "quarter": int(file.replace(".json", "")),
                        "name":    item["name"],
                        "count":   item["paymentInstruments"][0]["count"],
                        "amount":  item["paymentInstruments"][0]["amount"]
                    })
    df = pd.DataFrame(rows)
    save_to_sql(df, "aggregated_transaction", engine)
    add_indexes(engine, "aggregated_transaction", ["state", "year", "quarter"])


def load_aggregated_user(pulse_path, engine):
    rows = []
    path = os.path.join(pulse_path, "aggregated", "user", "country", "india", "state")
    for state in os.listdir(path):
        for year in os.listdir(os.path.join(path, state)):
            for file in os.listdir(os.path.join(path, state, year)):
                data = load_json(os.path.join(path, state, year, file))
                if not data:
                    continue
                for item in data["data"].get("usersByDevice") or []:
                    rows.append({
                        "state":      state,
                        "year":       int(year),
                        "quarter":    int(file.replace(".json", "")),
                        "brand":      item["brand"],
                        "count":      item["count"],
                        "percentage": item["percentage"]
                    })
    df = pd.DataFrame(rows)
    save_to_sql(df, "aggregated_user", engine)
    add_indexes(engine, "aggregated_user", ["state", "year", "quarter"])


def load_aggregated_insurance(pulse_path, engine):
    rows = []
    path = os.path.join(pulse_path, "aggregated", "insurance", "country", "india", "state")
    for state in os.listdir(path):
        for year in os.listdir(os.path.join(path, state)):
            for file in os.listdir(os.path.join(path, state, year)):
                data = load_json(os.path.join(path, state, year, file))
                if not data:
                    continue
                for item in data["data"].get("transactionData") or []:
                    instrument = item["paymentInstruments"][0]
                    rows.append({
                        "state":   state,
                        "year":    int(year),
                        "quarter": int(file.replace(".json", "")),
                        "name":    item["name"],
                        "count":   instrument["count"],
                        "amount":  instrument["amount"]
                    })
    df = pd.DataFrame(rows)
    save_to_sql(df, "aggregated_insurance", engine)
    add_indexes(engine, "aggregated_insurance", ["state", "year", "quarter"])


# ════════════════════════════════════════════════════════════════════
# MAP TABLES
# ════════════════════════════════════════════════════════════════════

def load_map_transaction(pulse_path, engine):
    rows = []
    path = os.path.join(pulse_path, "map", "transaction", "hover", "country", "india", "state")
    for state in os.listdir(path):
        for year in os.listdir(os.path.join(path, state)):
            for file in os.listdir(os.path.join(path, state, year)):
                data = load_json(os.path.join(path, state, year, file))
                if not data:
                    continue
                for item in data["data"].get("hoverDataList") or []:
                    rows.append({
                        "state":    state,
                        "year":     int(year),
                        "quarter":  int(file.replace(".json", "")),
                        "district": item["name"],
                        "count":    item["metric"][0]["count"],
                        "amount":   item["metric"][0]["amount"]
                    })
    df = pd.DataFrame(rows)
    save_to_sql(df, "map_transaction", engine)
    add_indexes(engine, "map_transaction", ["state", "year", "quarter"])


def load_map_user(pulse_path, engine):
    rows = []
    path = os.path.join(pulse_path, "map", "user", "hover", "country", "india", "state")
    for state in os.listdir(path):
        for year in os.listdir(os.path.join(path, state)):
            for file in os.listdir(os.path.join(path, state, year)):
                data = load_json(os.path.join(path, state, year, file))
                if not data:
                    continue
                for district, val in (data["data"].get("hoverData") or {}).items():
                    rows.append({
                        "state":            state,
                        "year":             int(year),
                        "quarter":          int(file.replace(".json", "")),
                        "district":         district,
                        "registered_users": val["registeredUsers"],
                        "app_opens":        val["appOpens"]
                    })
    df = pd.DataFrame(rows)
    save_to_sql(df, "map_user", engine)
    add_indexes(engine, "map_user", ["state", "year", "quarter"])


def load_map_insurance(pulse_path, engine):
    rows = []
    path = os.path.join(pulse_path, "map", "insurance", "hover", "country", "india", "state")
    for state in os.listdir(path):
        for year in os.listdir(os.path.join(path, state)):
            for file in os.listdir(os.path.join(path, state, year)):
                data = load_json(os.path.join(path, state, year, file))
                if not data:
                    continue
                for item in data["data"].get("hoverDataList") or []:
                    metric = item["metric"][0]
                    rows.append({
                        "state":    state,
                        "year":     int(year),
                        "quarter":  int(file.replace(".json", "")),
                        "district": item["name"],
                        "count":    metric["count"],
                        "amount":   metric["amount"]
                    })
    df = pd.DataFrame(rows)
    save_to_sql(df, "map_insurance", engine)
    add_indexes(engine, "map_insurance", ["state", "year", "quarter"])


# ════════════════════════════════════════════════════════════════════
# TOP TABLES
# ════════════════════════════════════════════════════════════════════

def load_top_transaction(pulse_path, engine):
    rows = []
    path = os.path.join(pulse_path, "top", "transaction", "country", "india", "state")
    for state in os.listdir(path):
        for year in os.listdir(os.path.join(path, state)):
            for file in os.listdir(os.path.join(path, state, year)):
                data = load_json(os.path.join(path, state, year, file))
                if not data:
                    continue
                for item in data["data"].get("pincodes") or []:
                    rows.append({
                        "state":       state,
                        "year":        int(year),
                        "quarter":     int(file.replace(".json", "")),
                        "entity_name": item["entityName"],
                        "count":       item["metric"]["count"],
                        "amount":      item["metric"]["amount"]
                    })
    df = pd.DataFrame(rows)
    save_to_sql(df, "top_transaction", engine)
    add_indexes(engine, "top_transaction", ["state", "year", "quarter"])


def load_top_user(pulse_path, engine):
    rows = []
    path = os.path.join(pulse_path, "top", "user", "country", "india", "state")
    for state in os.listdir(path):
        for year in os.listdir(os.path.join(path, state)):
            for file in os.listdir(os.path.join(path, state, year)):
                data = load_json(os.path.join(path, state, year, file))
                if not data:
                    continue
                for item in data["data"].get("pincodes") or []:
                    rows.append({
                        "state":            state,
                        "year":             int(year),
                        "quarter":          int(file.replace(".json", "")),
                        "entity_name":      item["name"],
                        "registered_users": item["registeredUsers"]
                    })
    df = pd.DataFrame(rows)
    save_to_sql(df, "top_user", engine)
    add_indexes(engine, "top_user", ["state", "year", "quarter"])


def load_top_insurance(pulse_path, engine):
    rows = []
    path = os.path.join(pulse_path, "top", "insurance", "country", "india", "state")
    for state in os.listdir(path):
        for year in os.listdir(os.path.join(path, state)):
            for file in os.listdir(os.path.join(path, state, year)):
                data = load_json(os.path.join(path, state, year, file))
                if not data:
                    continue
                for item in data["data"].get("districts") or []:
                    rows.append({
                        "state":       state,
                        "year":        int(year),
                        "quarter":     int(file.replace(".json", "")),
                        "entity_name": item["entityName"],
                        "count":       item["metric"]["count"],
                        "amount":      item["metric"]["amount"]
                    })
    df = pd.DataFrame(rows)
    save_to_sql(df, "top_insurance", engine)
    add_indexes(engine, "top_insurance", ["state", "year", "quarter"])


# ════════════════════════════════════════════════════════════════════
# MAIN — runs all loaders in order
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n📦 Starting PhonePe Pulse data extraction...\n")

    print("── Aggregated Tables ──────────────────────────")
    load_aggregated_transaction(PULSE_PATH, engine)
    load_aggregated_user(PULSE_PATH, engine)
    load_aggregated_insurance(PULSE_PATH, engine)

    print("\n── Map Tables ─────────────────────────────────")
    load_map_transaction(PULSE_PATH, engine)
    load_map_user(PULSE_PATH, engine)
    load_map_insurance(PULSE_PATH, engine)

    print("\n── Top Tables ─────────────────────────────────")
    load_top_transaction(PULSE_PATH, engine)
    load_top_user(PULSE_PATH, engine)
    load_top_insurance(PULSE_PATH, engine)

    print("\n🎉 All 9 tables loaded successfully!")