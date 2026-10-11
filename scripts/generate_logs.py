import numpy as np, pandas as pd
rng = np.random.default_rng(42)

users = [f"user{i:02d}" for i in range(1, 51)]
hosts = [f"PC{i:02d}" for i in range(1, 41)] + ["SRV01","SRV02","SRV03","SRV04","SRV05"]
days = pd.date_range("2026-09-01", periods=30)
rows = []

# Normal behavior: each user has 1-2 home PCs, works ~9-18h, few failures
for u in users:
    home = rng.choice(hosts[:40], size=rng.integers(1, 3), replace=False)
    start = rng.integers(8, 10)
    for d in days:
        if d.weekday() >= 5 and rng.random() > 0.1:
            continue
        for _ in range(rng.integers(2, 6)):
            t = d + pd.Timedelta(hours=int(rng.integers(start, start + 9)), minutes=int(rng.integers(0, 60)))
            rows.append((t, u, rng.choice(home), "success"))
        if rng.random() < 0.15:
            t = d + pd.Timedelta(hours=int(rng.integers(9, 17)), minutes=int(rng.integers(0, 60)))
            rows.append((t, u, rng.choice(home), "failure"))

# Hidden attackers (days 25-30 only)
attackers = {
    "user07": "lateral",    # logs on to many hosts quickly
    "user21": "offhours",   # logons at 1-4 AM
    "user33": "bruteforce", # burst of failures
    "user45": "newserver",  # touches servers it never used
}
for u, kind in attackers.items():
    for d in days[24:]:
        if kind == "lateral":
            for h in rng.choice(hosts, size=12, replace=False):
                t = d + pd.Timedelta(hours=14, minutes=int(rng.integers(0, 30)))
                rows.append((t, u, h, "success"))
        elif kind == "offhours":
            for _ in range(4):
                t = d + pd.Timedelta(hours=int(rng.integers(1, 5)), minutes=int(rng.integers(0, 60)))
                rows.append((t, u, rng.choice(hosts[:40]), "success"))
        elif kind == "bruteforce":
            for _ in range(40):
                t = d + pd.Timedelta(hours=11, minutes=int(rng.integers(0, 20)))
                rows.append((t, u, rng.choice(hosts[:40]), "failure"))
        elif kind == "newserver":
            for h in rng.choice(hosts[40:], size=3, replace=False):
                t = d + pd.Timedelta(hours=int(rng.integers(10, 16)), minutes=int(rng.integers(0, 60)))
                rows.append((t, u, h, "success"))

df = pd.DataFrame(rows, columns=["timestamp", "user", "host", "result"]).sort_values("timestamp")
df.to_csv("data/logons.csv", index=False)
print("rows:", len(df), "| users:", df.user.nunique())
