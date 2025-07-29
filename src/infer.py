# ----------------------------- infer.py (v5) -----------------------------
"""
Balanced Isolation-Forest  (captures over- *and* under-utilisation)
Outputs:
    • output/visit_scores.csv
    • output/sp_metrics.csv  (includes lat, lon, Insight-ready)
"""
import argparse, numpy as np, pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest

# -------------------------------------------------------------------------
def fit_score_visits(pq_path: str, contamination: float, n_estimators: int):
    df = pd.read_parquet(pq_path)

    # symmetric features
    df["inv_fill"]   = 1 - df["V_fill"]
    df["abs_z_fill"] = np.abs((df["V_fill"] - df["V_fill"].mean()) /
                              df["V_fill"].std())

    feat_cols = [c for c in df.columns if c not in ("service_point","visit_date")]
    X = df[feat_cols].fillna(df[feat_cols].median()).values

    iforest = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        max_samples="auto",
        bootstrap=True,
        random_state=42,
        n_jobs=-1,
    ).fit(X)

    df["anomaly_score"] = -iforest.score_samples(X)
    thresh = np.quantile(df["anomaly_score"], 1 - contamination)
    df["is_anomaly"] = (df["anomaly_score"] >= thresh).astype(int)
    return df

# -------------------------------------------------------------------------
def build_sp(df_vis: pd.DataFrame, contamination: float) -> pd.DataFrame:
    g = df_vis.groupby("service_point")
    sp = pd.DataFrame({
        "Service Point":     g.size().index,
        "Visit Count":       g.size().values,
        "Max Anomaly Score": g["anomaly_score"].max().values,
        "lat":               g["lat"].first(),
        "lon":               g["lon"].first(),
        "CAIv Ratio":        g["V_kg"].quantile(0.90) / g["capacity_kg"].first(),
        "VOF %":             g["V_fill"].apply(lambda s: (s > 1).mean()*100),
        "VUR %":             g["V_fill"].mean()*100,
        "CVv Ratio":         g["V_kg"].std() / g["V_kg"].mean(),
        "PMRv Ratio":        g["V_kg"].max() / g["V_kg"].mean(),
        "GR p90 (kg/day)":   g["GR"].quantile(0.90),
        "DtO (days)":        g["capacity_kg"].first() / g["GR"].median(),
        "IG (days)":         g["VI"].max(),
        "CVgr Ratio":        g["GR"].std() / g["GR"].mean(),
    })
    q = np.quantile(sp["Max Anomaly Score"], 1 - contamination)
    sp["Anomaly State"] = np.where(sp["Max Anomaly Score"] >= q, "Yes", "No")
    return sp

# -------------------------------------------------------------------------
def main(in_pq: str, contamination=0.05, n_estimators=400):
    df_vis = fit_score_visits(in_pq, contamination, n_estimators)
    Path("output").mkdir(exist_ok=True)
    df_vis.to_csv("output/visit_scores.csv", index=False)

    sp = build_sp(df_vis, contamination)
    sp.to_csv("output/sp_metrics.csv", index=False)
    print("✅ visit_scores.csv & sp_metrics.csv created in /output")

# -------------------------------------------------------------------------
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--in_pq", default="data/processed/visits.parquet")
    p.add_argument("--contam", type=float, default=0.05)
    p.add_argument("--n_estimators", type=int, default=400)
    args = p.parse_args()
    main(args.in_pq, args.contam, args.n_estimators)
