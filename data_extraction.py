"""
PhonePe Pulse - Data Extraction Script
Following Colab coding standards exactly:
  - Variable names: Agg_state_list, Agg_yr, Agg_yr_list
  - Column names:   State, Year, Quater, Transacion_type, Transacion_count, Transacion_amount
  - Loop style:     for i in state_list → for j in years → for k in quarters
"""

import os
import json
import pandas as pd
from sqlalchemy import create_engine

# ── DB Config ─────────────────────────────────────────────────────────────────
engine = create_engine("mysql+mysqlconnector://root:Deepika93@localhost/phonepe_pulse")

# ── Base path (your local cloned pulse data) ──────────────────────────────────
BASE = r"C:\Users\Palani\Desktop\Meenakshi\PhonePay\pulse\data"

def to_sql(df, table_name):
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"  ✅  {table_name:30s} → {len(df):,} rows loaded")


# ══════════════════════════════════════════════════════════════════════════════
#  1.  AGGREGATED TRANSACTION
#      DataFrame : Agg_Trans
#      Columns   : State, Year, Quater, Transacion_type,
#                  Transacion_count, Transacion_amount
# ══════════════════════════════════════════════════════════════════════════════
def load_agg_transaction():
    path = os.path.join(BASE, "aggregated", "transaction", "country", "india", "state")

    # This is to direct the path to get the data as states
    Agg_state_list = os.listdir(path)

    # clm dict to extract the data and create a dataframe
    clm = {
        'State':            [],
        'Year':             [],
        'Quater':           [],
        'Transacion_type':  [],
        'Transacion_count': [],
        'Transacion_amount':[]
    }

    for i in Agg_state_list:                          # i = state
        p_i = os.path.join(path, i)
        Agg_yr = os.listdir(p_i)
        for j in Agg_yr:                              # j = year
            p_j = os.path.join(p_i, j)
            Agg_yr_list = os.listdir(p_j)
            for k in Agg_yr_list:                     # k = quarter file
                p_k = os.path.join(p_j, k)
                Data = open(p_k, 'r')
                D = json.load(Data)
                for z in D['data']['transactionData']:
                    Name   = z['name']
                    count  = z['paymentInstruments'][0]['count']
                    amount = z['paymentInstruments'][0]['amount']
                    clm['Transacion_type'].append(Name)
                    clm['Transacion_count'].append(count)
                    clm['Transacion_amount'].append(amount)
                    clm['State'].append(i)
                    clm['Year'].append(j)
                    clm['Quater'].append(int(k.strip('.json')))

    # Successfully created a dataframe
    Agg_Trans = pd.DataFrame(clm)
    to_sql(Agg_Trans, "aggregated_transaction")
    return Agg_Trans


# ══════════════════════════════════════════════════════════════════════════════
#  2.  AGGREGATED USER
#      DataFrame : Agg_User
#      Columns   : State, Year, Quater, Brands, Count, Percentage,
#                  Registered_user, App_opens
# ══════════════════════════════════════════════════════════════════════════════
def load_agg_user():
    path = os.path.join(BASE, "aggregated", "user", "country", "india", "state")

    Agg_state_list = os.listdir(path)

    clm = {
        'State':           [],
        'Year':            [],
        'Quater':          [],
        'Brands':          [],
        'Count':           [],
        'Percentage':      [],
        'Registered_user': [],
        'App_opens':       []
    }

    for i in Agg_state_list:
        p_i = os.path.join(path, i)
        Agg_yr = os.listdir(p_i)
        for j in Agg_yr:
            p_j = os.path.join(p_i, j)
            Agg_yr_list = os.listdir(p_j)
            for k in Agg_yr_list:
                p_k = os.path.join(p_j, k)
                Data = open(p_k, 'r')
                D = json.load(Data)
                registered = D['data']['aggregated']['registeredUsers']
                app_opens  = D['data']['aggregated']['appOpens']
                brands     = D['data'].get('usersByDevice')
                if brands:
                    for z in brands:
                        clm['Brands'].append(z['brand'])
                        clm['Count'].append(z['count'])
                        clm['Percentage'].append(z['percentage'])
                        clm['State'].append(i)
                        clm['Year'].append(j)
                        clm['Quater'].append(int(k.strip('.json')))
                        clm['Registered_user'].append(registered)
                        clm['App_opens'].append(app_opens)
                else:
                    clm['Brands'].append(None)
                    clm['Count'].append(0)
                    clm['Percentage'].append(0)
                    clm['State'].append(i)
                    clm['Year'].append(j)
                    clm['Quater'].append(int(k.strip('.json')))
                    clm['Registered_user'].append(registered)
                    clm['App_opens'].append(app_opens)

    Agg_User = pd.DataFrame(clm)
    to_sql(Agg_User, "aggregated_user")
    return Agg_User


# ══════════════════════════════════════════════════════════════════════════════
#  3.  AGGREGATED INSURANCE
#      DataFrame : Agg_Insurance
#      Columns   : State, Year, Quater, Transacion_type,
#                  Transacion_count, Transacion_amount
# ══════════════════════════════════════════════════════════════════════════════
def load_agg_insurance():
    path = os.path.join(BASE, "aggregated", "insurance", "country", "india", "state")

    if not os.path.exists(path):
        print("  ⚠️   aggregated/insurance folder not found — skipping")
        return pd.DataFrame()

    Agg_state_list = os.listdir(path)

    clm = {
        'State':            [],
        'Year':             [],
        'Quater':           [],
        'Transacion_type':  [],
        'Transacion_count': [],
        'Transacion_amount':[]
    }

    for i in Agg_state_list:
        p_i = os.path.join(path, i)
        Agg_yr = os.listdir(p_i)
        for j in Agg_yr:
            p_j = os.path.join(p_i, j)
            Agg_yr_list = os.listdir(p_j)
            for k in Agg_yr_list:
                p_k = os.path.join(p_j, k)
                Data = open(p_k, 'r')
                D = json.load(Data)
                for z in D['data']['transactionData']:
                    Name   = z['name']
                    count  = z['paymentInstruments'][0]['count']
                    amount = z['paymentInstruments'][0]['amount']
                    clm['Transacion_type'].append(Name)
                    clm['Transacion_count'].append(count)
                    clm['Transacion_amount'].append(amount)
                    clm['State'].append(i)
                    clm['Year'].append(j)
                    clm['Quater'].append(int(k.strip('.json')))

    Agg_Insurance = pd.DataFrame(clm)
    to_sql(Agg_Insurance, "aggregated_insurance")
    return Agg_Insurance


# ══════════════════════════════════════════════════════════════════════════════
#  4.  MAP TRANSACTION
#      DataFrame : Map_Trans
#      Columns   : State, Year, Quater, District,
#                  Count, Amount
# ══════════════════════════════════════════════════════════════════════════════
def load_map_transaction():
    path = os.path.join(BASE, "map", "transaction", "hover", "country", "india", "state")

    Agg_state_list = os.listdir(path)

    clm = {
        'State':    [],
        'Year':     [],
        'Quater':   [],
        'District': [],
        'Count':    [],
        'Amount':   []
    }

    for i in Agg_state_list:
        p_i = os.path.join(path, i)
        Agg_yr = os.listdir(p_i)
        for j in Agg_yr:
            p_j = os.path.join(p_i, j)
            Agg_yr_list = os.listdir(p_j)
            for k in Agg_yr_list:
                p_k = os.path.join(p_j, k)
                Data = open(p_k, 'r')
                D = json.load(Data)
                for z in D['data']['hoverDataList']:
                    District = z['name']
                    count    = z['metric'][0]['count']
                    amount   = z['metric'][0]['amount']
                    clm['District'].append(District)
                    clm['Count'].append(count)
                    clm['Amount'].append(amount)
                    clm['State'].append(i)
                    clm['Year'].append(j)
                    clm['Quater'].append(int(k.strip('.json')))

    Map_Trans = pd.DataFrame(clm)
    to_sql(Map_Trans, "map_transaction")
    return Map_Trans


# ══════════════════════════════════════════════════════════════════════════════
#  5.  MAP USER
#      DataFrame : Map_User
#      Columns   : State, Year, Quater, District,
#                  Registered_user, App_opens
# ══════════════════════════════════════════════════════════════════════════════
def load_map_user():
    path = os.path.join(BASE, "map", "user", "hover", "country", "india", "state")

    Agg_state_list = os.listdir(path)

    clm = {
        'State':           [],
        'Year':            [],
        'Quater':          [],
        'District':        [],
        'Registered_user': [],
        'App_opens':       []
    }

    for i in Agg_state_list:
        p_i = os.path.join(path, i)
        Agg_yr = os.listdir(p_i)
        for j in Agg_yr:
            p_j = os.path.join(p_i, j)
            Agg_yr_list = os.listdir(p_j)
            for k in Agg_yr_list:
                p_k = os.path.join(p_j, k)
                Data = open(p_k, 'r')
                D = json.load(Data)
                for district, val in D['data']['hoverData'].items():
                    clm['District'].append(district)
                    clm['Registered_user'].append(val['registeredUsers'])
                    clm['App_opens'].append(val['appOpens'])
                    clm['State'].append(i)
                    clm['Year'].append(j)
                    clm['Quater'].append(int(k.strip('.json')))

    Map_User = pd.DataFrame(clm)
    to_sql(Map_User, "map_user")
    return Map_User


# ══════════════════════════════════════════════════════════════════════════════
#  6.  MAP INSURANCE
#      DataFrame : Map_Insurance
#      Columns   : State, Year, Quater, District, Count, Amount
# ══════════════════════════════════════════════════════════════════════════════
def load_map_insurance():
    path = os.path.join(BASE, "map", "insurance", "hover", "country", "india", "state")

    if not os.path.exists(path):
        print("  ⚠️   map/insurance folder not found — skipping")
        return pd.DataFrame()

    Agg_state_list = os.listdir(path)

    clm = {
        'State':    [],
        'Year':     [],
        'Quater':   [],
        'District': [],
        'Count':    [],
        'Amount':   []
    }

    for i in Agg_state_list:
        p_i = os.path.join(path, i)
        Agg_yr = os.listdir(p_i)
        for j in Agg_yr:
            p_j = os.path.join(p_i, j)
            Agg_yr_list = os.listdir(p_j)
            for k in Agg_yr_list:
                p_k = os.path.join(p_j, k)
                Data = open(p_k, 'r')
                D = json.load(Data)
                for z in D['data']['hoverDataList']:
                    clm['District'].append(z['name'])
                    clm['Count'].append(z['metric'][0]['count'])
                    clm['Amount'].append(z['metric'][0]['amount'])
                    clm['State'].append(i)
                    clm['Year'].append(j)
                    clm['Quater'].append(int(k.strip('.json')))

    Map_Insurance = pd.DataFrame(clm)
    to_sql(Map_Insurance, "map_insurance")
    return Map_Insurance


# ══════════════════════════════════════════════════════════════════════════════
#  7.  TOP TRANSACTION
#      DataFrame : Top_Trans
#      Columns   : State, Year, Quater, EntityType,
#                  EntityName, Count, Amount
# ══════════════════════════════════════════════════════════════════════════════
def load_top_transaction():
    path = os.path.join(BASE, "top", "transaction", "country", "india", "state")

    Agg_state_list = os.listdir(path)

    clm = {
        'State':      [],
        'Year':       [],
        'Quater':     [],
        'EntityType': [],
        'EntityName': [],
        'Count':      [],
        'Amount':     []
    }

    for i in Agg_state_list:
        p_i = os.path.join(path, i)
        Agg_yr = os.listdir(p_i)
        for j in Agg_yr:
            p_j = os.path.join(p_i, j)
            Agg_yr_list = os.listdir(p_j)
            for k in Agg_yr_list:
                p_k = os.path.join(p_j, k)
                Data = open(p_k, 'r')
                D = json.load(Data)
                for entity_key, label in [('districts', 'District'), ('pincodes', 'Pincode')]:
                    for z in D['data'].get(entity_key, []):
                        clm['EntityType'].append(label)
                        clm['EntityName'].append(z['entityName'])
                        clm['Count'].append(z['metric']['count'])
                        clm['Amount'].append(z['metric']['amount'])
                        clm['State'].append(i)
                        clm['Year'].append(j)
                        clm['Quater'].append(int(k.strip('.json')))

    Top_Trans = pd.DataFrame(clm)
    to_sql(Top_Trans, "top_transaction")
    return Top_Trans


# ══════════════════════════════════════════════════════════════════════════════
#  8.  TOP USER
#      DataFrame : Top_User
#      Columns   : State, Year, Quater, EntityType, EntityName, Registered_user
# ══════════════════════════════════════════════════════════════════════════════
def load_top_user():
    path = os.path.join(BASE, "top", "user", "country", "india", "state")

    Agg_state_list = os.listdir(path)

    clm = {
        'State':           [],
        'Year':            [],
        'Quater':          [],
        'EntityType':      [],
        'EntityName':      [],
        'Registered_user': []
    }

    for i in Agg_state_list:
        p_i = os.path.join(path, i)
        Agg_yr = os.listdir(p_i)
        for j in Agg_yr:
            p_j = os.path.join(p_i, j)
            Agg_yr_list = os.listdir(p_j)
            for k in Agg_yr_list:
                p_k = os.path.join(p_j, k)
                Data = open(p_k, 'r')
                D = json.load(Data)
                for entity_key, label in [('districts', 'District'), ('pincodes', 'Pincode')]:
                    for z in D['data'].get(entity_key, []):
                        clm['EntityType'].append(label)
                        clm['EntityName'].append(z['name'])
                        clm['Registered_user'].append(z['registeredUsers'])
                        clm['State'].append(i)
                        clm['Year'].append(j)
                        clm['Quater'].append(int(k.strip('.json')))

    Top_User = pd.DataFrame(clm)
    to_sql(Top_User, "top_user")
    return Top_User


# ══════════════════════════════════════════════════════════════════════════════
#  9.  TOP INSURANCE
#      DataFrame : Top_Insurance
#      Columns   : State, Year, Quater, EntityType, EntityName, Count, Amount
# ══════════════════════════════════════════════════════════════════════════════
def load_top_insurance():
    path = os.path.join(BASE, "top", "insurance", "country", "india", "state")

    if not os.path.exists(path):
        print("  ⚠️   top/insurance folder not found — skipping")
        return pd.DataFrame()

    Agg_state_list = os.listdir(path)

    clm = {
        'State':      [],
        'Year':       [],
        'Quater':     [],
        'EntityType': [],
        'EntityName': [],
        'Count':      [],
        'Amount':     []
    }

    for i in Agg_state_list:
        p_i = os.path.join(path, i)
        Agg_yr = os.listdir(p_i)
        for j in Agg_yr:
            p_j = os.path.join(p_i, j)
            Agg_yr_list = os.listdir(p_j)
            for k in Agg_yr_list:
                p_k = os.path.join(p_j, k)
                Data = open(p_k, 'r')
                D = json.load(Data)
                for entity_key, label in [('districts', 'District'), ('pincodes', 'Pincode')]:
                    for z in D['data'].get(entity_key, []):
                        clm['EntityType'].append(label)
                        clm['EntityName'].append(z['entityName'])
                        clm['Count'].append(z['metric']['count'])
                        clm['Amount'].append(z['metric']['amount'])
                        clm['State'].append(i)
                        clm['Year'].append(j)
                        clm['Quater'].append(int(k.strip('.json')))

    Top_Insurance = pd.DataFrame(clm)
    to_sql(Top_Insurance, "top_insurance")
    return Top_Insurance


# ── Run All ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 PhonePe Pulse — Data Extraction Started\n" + "="*50)
    load_agg_transaction()
    load_agg_user()
    load_agg_insurance()
    load_map_transaction()
    load_map_user()
    load_map_insurance()
    load_top_transaction()
    load_top_user()
    load_top_insurance()
    print("="*50)
    print("🎉 All 9 tables loaded into MySQL  →  phonepe_pulse\n")
