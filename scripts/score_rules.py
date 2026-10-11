import pandas as pd, numpy as np

feat = pd.read_csv("data/features.csv", parse_dates=["date"])
cols = ["logons", "distinct_hosts", "server_logons", "offhours", "failures"]
cutoff = pd.Timestamp("2026-09-25")
base = feat[feat.date < cutoff]
test = feat[feat.date >= cutoff].copy()

# Per-user baseline: mean, std, and the set of servers/hosts ever used
m = base.groupby("user")[cols].mean().add_suffix("_mean")
s = base.groupby("user")[cols].std().add_suffix("_std")
test = test.merge(m, on="user").merge(s, on="user")

# Z-score with a floor on std so tiny baselines don't explode scores
for c in cols:
    std = test[c + "_std"].fillna(0).clip(lower=1.0)
    test["z_" + c] = ((test[c] - test[c + "_mean"]) / std).clip(lower=0)

# Rare-event rules
test["rule_offhours"] = (test.offhours > 0) & (test.offhours_mean < 0.5)
test["rule_new_server"] = (test.server_logons > 0) & (test.server_logons_mean < 0.1)
test["rule_failure_burst"] = test.failures >= 10
test["rule_many_hosts"] = test.distinct_hosts >= 6

zc = ["z_" + c for c in cols]
rc = ["rule_offhours", "rule_new_server", "rule_failure_burst", "rule_many_hosts"]
test["z_score"] = test[zc].sum(axis=1)
test["rule_hits"] = test[rc].sum(axis=1)
test["risk"] = test.z_score + 5 * test.rule_hits

test.to_csv("data/scored_days.csv", index=False)

top = (test.groupby("user")
       .agg(max_risk=("risk", "max"), avg_risk=("risk", "mean"), rule_hits=("rule_hits", "sum"))
       .sort_values("max_risk", ascending=False).head(10).round(1))
print(top)
