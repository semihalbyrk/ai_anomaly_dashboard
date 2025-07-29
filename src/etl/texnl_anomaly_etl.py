# ----------------------------- texnl_anomaly_etl.py -----------------------------
"""
ETL + feature engineering
Input : Excel (Task Record · Service Points · Assets)
Output: visits.parquet  – one row per visit, incl. latitude / longitude
"""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np

# candidate column names that carry the SP name
COL_SP_CANDIDATES_SP = {
    "Service Point", "Service Point Name",
    "Service point", "service_point", "Name"
}

# -------------------------------------------------------------------------
def run_etl(input_xlsx: str, out_pq: str):
    xlsx = pd.ExcelFile(input_xlsx, engine="openpyxl")

    # ---------- load sheets ----------
    tasks   = pd.read_excel(xlsx, sheet_name="Task Record")
    assets  = pd.read_excel(xlsx, sheet_name="Assets")

    # ---------- Service-Points sheet (lat / lon) ----------
    sp_sheet = pd.read_excel(xlsx, sheet_name="Service Points")
    lat_col = [c for c in sp_sheet.columns if c.lower() in {"latitude", "lat"}][0]
    lon_col = [c for c in sp_sheet.columns if c.lower() in {"longitude", "lon"}][0]
    name_col = [c for c in sp_sheet.columns if c.strip() in COL_SP_CANDIDATES_SP][0]

    sp_sheet = sp_sheet.rename(columns={name_col: "service_point",
                                        lat_col: "lat",
                                        lon_col: "lon"})
    sp_geo = sp_sheet[["service_point", "lat", "lon"]]

    # ---------- clean Task table ----------
    tasks = tasks[tasks["Material"].str.contains("Bag Weight", na=False)].copy()
    tasks["visit_date"] = pd.to_datetime(tasks["Date"]).dt.date
    tasks = tasks.rename(columns={"Actual Amount (Item)": "V_kg",
                                  "Service Point": "service_point"})
    tasks["V_kg"] = tasks["V_kg"].astype(float)

    # ---------- capacity per SP ----------
    assets = assets.rename(columns={"Location Details": "service_point",
                                    "Weight Capacity": "capacity_kg"})
    assets["capacity_kg"] = assets["capacity_kg"].astype(float)
    cap = assets.groupby("service_point", as_index=False)["capacity_kg"].sum()

    # ---------- merge & daily aggregate ----------
    df = (
        tasks.groupby(["service_point", "visit_date"], as_index=False)["V_kg"].sum()
             .merge(cap, how="left", on="service_point")
             .merge(sp_geo, how="left", on="service_point")      # ← geo
             .dropna(subset=["capacity_kg"])
    )

    df["V_fill"] = df["V_kg"] / df["capacity_kg"]

    # ---------- interval features ----------
    df["visit_date"] = pd.to_datetime(df["visit_date"])
    df = df.sort_values(["service_point", "visit_date"])
    df["VI"] = (
        df.groupby("service_point")["visit_date"]
          .diff().dt.days.fillna(0).replace(0, np.nan)
    )
    df["GR"] = df["V_kg"] / df["VI"]

    # rolling stats
    df["V_kg_mean"] = (
        df.groupby("service_point")["V_kg"]
          .transform(lambda s: s.rolling(6, min_periods=1).mean())
    )
    df["V_kg_std"] = (
        df.groupby("service_point")["V_kg"]
          .transform(lambda s: s.rolling(6, min_periods=1).std().fillna(0))
    )

    df.to_parquet(out_pq, index=False)
    print(f"✅ visits parquet written → {out_pq}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--out",   required=True)
    args = p.parse_args()
    run_etl(args.input, args.out)
