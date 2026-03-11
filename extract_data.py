import os
import json
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# DB Connection

engine = create_engine("mysql+mysqlconnector://root:Deepika93@localhost/phonepe_pulse")

pulse_path = "pulse/data"

# ── Aggregated Transaction ──────────────────────────────────────────
rows = []
path = os.path.join(pulse_path, "aggregated", "transaction", "country", "india", "state")
for state in os.listdir(path):
    for year in os.listdir(os.path.join(path, state)):
        for file in os.listdir(os.path.join(path, state, year)):
            with open(os.path.join(path, state, year, file)) as f:
                data = json.load(f)
            for item in data["data"]["transactionData"]:
                rows.append({
                    "state": state, "year": int(year),
                    "quarter": int(file.replace(".json", "")),
                    "name": item["name"],
                    "count": item["paymentInstruments"][0]["count"],
                    "amount": item["paymentInstruments"][0]["amount"]
                })
df = pd.DataFrame(rows)
df.to_sql("aggregated_transaction", con=engine, if_exists="replace", index=False)
print(f"aggregated_transaction: {len(df)} rows loaded ✅")

# ── Aggregated User ─────────────────────────────────────────────────
rows = []
path = os.path.join(pulse_path, "aggregated", "user", "country", "india", "state")
for state in os.listdir(path):
    for year in os.listdir(os.path.join(path, state)):
        for file in os.listdir(os.path.join(path, state, year)):
            with open(os.path.join(path, state, year, file)) as f:
                data = json.load(f)
            brands = data["data"].get("usersByDevice") or []
            for item in brands:
                rows.append({
                    "state": state, "year": int(year),
                    "quarter": int(file.replace(".json", "")),
                    "brand": item["brand"],
                    "count": item["count"],
                    "percentage": item["percentage"]
                })
df = pd.DataFrame(rows)
df.to_sql("aggregated_user", con=engine, if_exists="replace", index=False)
print(f"aggregated_user: {len(df)} rows loaded ✅")

# ── Map Transaction ─────────────────────────────────────────────────
rows = []
path = os.path.join(pulse_path, "map", "transaction", "hover", "country", "india", "state")
for state in os.listdir(path):
    for year in os.listdir(os.path.join(path, state)):
        for file in os.listdir(os.path.join(path, state, year)):
            with open(os.path.join(path, state, year, file)) as f:
                data = json.load(f)
            for item in data["data"]["hoverDataList"]:
                rows.append({
                    "state": state, "year": int(year),
                    "quarter": int(file.replace(".json", "")),
                    "district": item["name"],
                    "count": item["metric"][0]["count"],
                    "amount": item["metric"][0]["amount"]
                })
df = pd.DataFrame(rows)
df.to_sql("map_transaction", con=engine, if_exists="replace", index=False)
print(f"map_transaction: {len(df)} rows loaded ✅")

# ── Map User ────────────────────────────────────────────────────────
rows = []
path = os.path.join(pulse_path, "map", "user", "hover", "country", "india", "state")
for state in os.listdir(path):
    for year in os.listdir(os.path.join(path, state)):
        for file in os.listdir(os.path.join(path, state, year)):
            with open(os.path.join(path, state, year, file)) as f:
                data = json.load(f)
            for district, val in data["data"]["hoverData"].items():
                rows.append({
                    "state": state, "year": int(year),
                    "quarter": int(file.replace(".json", "")),
                    "district": district,
                    "registered_users": val["registeredUsers"],
                    "app_opens": val["appOpens"]
                })
df = pd.DataFrame(rows)
df.to_sql("map_user", con=engine, if_exists="replace", index=False)
print(f"map_user: {len(df)} rows loaded ✅")

# ── Top Transaction ─────────────────────────────────────────────────
rows = []
path = os.path.join(pulse_path, "top", "transaction", "country", "india", "state")
for state in os.listdir(path):
    for year in os.listdir(os.path.join(path, state)):
        for file in os.listdir(os.path.join(path, state, year)):
            with open(os.path.join(path, state, year, file)) as f:
                data = json.load(f)
            for item in data["data"]["pincodes"]:
                rows.append({
                    "state": state, "year": int(year),
                    "quarter": int(file.replace(".json", "")),
                    "entity_name": item["entityName"],
                    "count": item["metric"]["count"],
                    "amount": item["metric"]["amount"]
                })
df = pd.DataFrame(rows)
df.to_sql("top_transaction", con=engine, if_exists="replace", index=False)
print(f"top_transaction: {len(df)} rows loaded ✅")

# ── Top User ────────────────────────────────────────────────────────
rows = []
path = os.path.join(pulse_path, "top", "user", "country", "india", "state")
for state in os.listdir(path):
    for year in os.listdir(os.path.join(path, state)):
        for file in os.listdir(os.path.join(path, state, year)):
            with open(os.path.join(path, state, year, file)) as f:
                data = json.load(f)
            for item in data["data"]["pincodes"]:
                rows.append({
                    "state": state, "year": int(year),
                    "quarter": int(file.replace(".json", "")),
                    "entity_name": item["name"],
                    "registered_users": item["registeredUsers"]
                })
df = pd.DataFrame(rows)
df.to_sql("top_user", con=engine, if_exists="replace", index=False)
print(f"top_user: {len(df)} rows loaded ✅")

print("\nAll tables loaded successfully! 🎉")