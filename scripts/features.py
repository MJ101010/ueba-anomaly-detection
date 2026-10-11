import pandas as pd

df = pd.read_csv("data/logons.csv", parse_dates=["timestamp"])
df["date"] = df.timestamp.dt.normalize()
df["hour"] = df.timestamp.dt.hour
df["is_server"] = df.host.str.startswith("SRV")
df["is_off"] = (df.hour >= 22) | (df.hour < 6)
ok = df[df.result == "success"]
bad = df[df.result == "failure"]

feat = ok.groupby(["user", "date"]).agg(
    logons=("host", "size"),
    distinct_hosts=("host", "nunique"),
    server_logons=("is_server", "sum"),
    offhours=("is_off", "sum"),
)
feat["failures"] = bad.groupby(["user", "date"]).size()
feat = feat.reset_index().fillna(0)

# Include user-days that had only failures (e.g. brute force)
only_fail = bad.groupby(["user", "date"]).size().rename("failures").reset_index()
feat = feat.merge(only_fail, on=["user", "date"], how="outer", suffixes=("", "_f"))
feat["failures"] = feat["failures_f"].fillna(feat["failures"])
feat = feat.drop(columns="failures_f").fillna(0)

feat.to_csv("data/features.csv", index=False)

cutoff = pd.Timestamp("2026-09-25")
base = feat[feat.date < cutoff]
stats = base.groupby("user")[["logons", "distinct_hosts", "server_logons", "offhours", "failures"]].agg(["mean", "std"])
stats.to_csv("data/baseline_stats.csv")

print("feature rows:", len(feat))
print("baseline rows:", len(base), "| test rows:", len(feat) - len(base))
print(base[["logons", "distinct_hosts", "server_logons", "offhours", "failures"]].describe().loc[["mean", "std", "max"]].round(2))
