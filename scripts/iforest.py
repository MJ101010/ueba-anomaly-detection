import pandas as pd, numpy as np
from sklearn.ensemble import IsolationForest

feat = pd.read_csv("data/features.csv", parse_dates=["date"])
cols = ["logons", "distinct_hosts", "server_logons", "offhours", "failures"]
cutoff = pd.Timestamp("2026-09-25")
base = feat[feat.date < cutoff]
test = pd.read_csv("data/scored_days.csv", parse_dates=["date"])

# Train ONLY on baseline (normal) days
model = IsolationForest(n_estimators=200, contamination="auto", random_state=42)
model.fit(base[cols])

# Higher = more anomalous (flip sklearn's sign convention)
test["if_score"] = -model.score_samples(test[cols])

# Scale to 0-10 so it can be combined with the rule-based risk later
lo, hi = test.if_score.min(), test.if_score.max()
test["if_scaled"] = 10 * (test.if_score - lo) / (hi - lo)

test.to_csv("data/scored_days.csv", index=False)

top = (test.groupby("user")
       .agg(max_if=("if_scaled", "max"), avg_if=("if_scaled", "mean"))
       .sort_values("max_if", ascending=False).head(10).round(2))
print(top)
