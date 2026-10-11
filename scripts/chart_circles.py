import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

t = pd.read_csv("data/scored_days.csv", parse_dates=["date"])
t["risk_scaled"] = 10 * t.risk / t.risk.max()
t["final"] = 0.7 * t.risk_scaled + 0.3 * t.if_scaled   # use 0.5/0.5 if you did not do Step 8

peak = t.loc[t.groupby("user").final.idxmax()].copy()
attackers = {"user07", "user21", "user33", "user45"}
peak["is_attacker"] = peak.user.isin(attackers)

fig, ax = plt.subplots(figsize=(10, 6.5))
normal = peak[~peak.is_attacker]
att = peak[peak.is_attacker]

ax.scatter(normal.risk_scaled, normal.if_scaled, s=60 + normal.final * 60,
           c="#95a5a6", alpha=0.6, edgecolors="white", linewidths=1, label="Normal user")
ax.scatter(att.risk_scaled, att.if_scaled, s=150 + att.final * 140,
           c="#e74c3c", alpha=0.85, edgecolors="black", linewidths=1.2, label="Injected attacker")

# Label the attackers and the 5 highest-scoring normal users (false positives)
offsets = [(-10, 22), (12, -26), (10, 18), (-12, -28)]
for i, r in enumerate(att.sort_values("risk_scaled").itertuples()):
    ax.annotate(r.user, (r.risk_scaled, r.if_scaled), xytext=offsets[i % 4], textcoords="offset points",
                fontsize=9, fontweight="bold", color="#922b21", ha="center")
shift = [(28, 10), (28, -12), (30, 8), (30, -10), (28, 8)]
for i, r in enumerate(normal.sort_values("final", ascending=False).head(5).itertuples()):
    ax.annotate(r.user, (r.risk_scaled, r.if_scaled), xytext=shift[i], textcoords="offset points",
                fontsize=8, color="#555555", ha="center")

ax.set_xlabel("Rule-based risk (0-10): explainable rules + z-scores")
ax.set_ylabel("Isolation Forest score (0-10): ML anomaly score")
ax.set_title("Mini UEBA: each circle is a user (circle size = final risk score)")
ax.grid(alpha=0.25)
ax.legend(loc="upper right", markerscale=0.5)
plt.tight_layout()
plt.savefig("output/top_risky_users_circles.png", dpi=150)
print("Saved: output/top_risky_users_circles.png")
