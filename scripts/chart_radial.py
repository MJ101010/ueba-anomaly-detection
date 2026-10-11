import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

t = pd.read_csv("data/scored_days.csv", parse_dates=["date"])
t["risk_scaled"] = 10 * t.risk / t.risk.max()
t["final"] = 0.7 * t.risk_scaled + 0.3 * t.if_scaled   # use 0.5/0.5 if you did not do Step 8

peak = t.loc[t.groupby("user").final.idxmax()]
top = peak.sort_values("final", ascending=False).head(10).reset_index(drop=True)
attackers = {"user07", "user21", "user33", "user45"}

n = len(top)
max_angle = 1.5 * np.pi                     # each ring is at most 270 degrees
angles = top.final / 10 * max_angle
colors = ["#e74c3c" if u in attackers else "#7f8c8d" for u in top.user]

fig = plt.figure(figsize=(8.5, 8.5))
ax = fig.add_subplot(111, projection="polar")
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)

# Ring i: rank 1 is the outer ring, rank 10 is the inner ring
radius = np.arange(n)[::-1] + 3             # leave a hole in the middle
ax.barh(radius, [max_angle] * n, height=0.72, color="#ecf0f1", edgecolor="none")   # background track
ax.barh(radius, angles, height=0.72, color=colors, edgecolor="white")              # score arc

for r, row in zip(radius, top.itertuples()):
    tag = " (attacker)" if row.user in attackers else ""
    ax.text(-0.04, r, f"{row.user}{tag}  {row.final:.1f}", ha="right", va="center", fontsize=9)

ax.set_ylim(0, n + 3.5)
ax.set_yticks([]); ax.set_xticks([]); ax.spines["polar"].set_visible(False); ax.grid(False)
ax.set_title("Mini UEBA: top 10 risky users (arc length = final risk score)\nred = injected attacker, grey = normal user",
             fontsize=12, pad=22)
plt.tight_layout()
plt.savefig("output/top_risky_users_radial.png", dpi=150)
print("Saved: output/top_risky_users_radial.png")
