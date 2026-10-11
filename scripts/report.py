import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

t = pd.read_csv("data/scored_days.csv", parse_dates=["date"])
t["risk_scaled"] = 10 * t.risk / t.risk.max()
t["final"] = 0.5 * t.risk_scaled + 0.5 * t.if_scaled

rules = {"rule_offhours": "off-hours logon", "rule_new_server": "new server access",
         "rule_failure_burst": "failure burst", "rule_many_hosts": "many hosts in a day"}
zmap = {"z_logons": "logon volume", "z_distinct_hosts": "host count", "z_server_logons": "server logons",
        "z_offhours": "off-hours logons", "z_failures": "failures"}

def why(row):
    parts = [v for k, v in rules.items() if row[k]]
    zc = max(zmap, key=lambda c: row[c])
    if row[zc] > 3:
        parts.append(f"high {zmap[zc]} (z={row[zc]:.1f})")
    return "; ".join(parts) or "statistical outlier only"

peak = t.loc[t.groupby("user").final.idxmax()].copy()
peak["why"] = peak.apply(why, axis=1)
flagged = t[t.final >= 5].groupby("user").size()
peak["days_flagged"] = peak.user.map(flagged).fillna(0).astype(int)

top = (peak.sort_values("final", ascending=False).head(10)
       [["user", "final", "risk_scaled", "if_scaled", "days_flagged", "why"]].round(2))
top.to_csv("output/top_risky_users.csv", index=False)
print(top.to_string(index=False))

# Self-check against the hidden attackers
attackers = {"user07", "user21", "user33", "user45"}
top4 = set(top.head(4).user)
top10 = set(top.user)
print("\nAttackers in top 4 :", sorted(top4 & attackers), f"({len(top4 & attackers)}/4)")
print("Attackers in top 10:", sorted(top10 & attackers), f"({len(top10 & attackers)}/4)")
print("False positives in top 10:", sorted(top10 - attackers))

# Chart
colors = ["#c0392b" if u in attackers else "#7f8c8d" for u in top.user]
plt.figure(figsize=(9, 5))
plt.barh(top.user[::-1], top.final[::-1], color=colors[::-1])
plt.xlabel("Final risk score (0-10)")
plt.title("Top 10 risky users (red = injected attacker)")
plt.tight_layout()
plt.savefig("output/top_risky_users.png", dpi=150)

# Markdown report
lines = ["# Mini UEBA Report", "",
         "Baseline: 2026-09-01 to 2026-09-24. Test period: 2026-09-25 to 2026-09-30.", "",
         "| Rank | User | Final | Rules | Model | Days flagged | Why |", "|---|---|---|---|---|---|---|"]
for i, r in enumerate(top.itertuples(), 1):
    lines.append(f"| {i} | {r.user} | {r.final} | {r.risk_scaled} | {r.if_scaled} | {r.days_flagged} | {r.why} |")
open("output/report.md", "w").write("\n".join(lines))
print("\nSaved: output/top_risky_users.csv, top_risky_users.png, report.md")
