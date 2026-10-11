\# Anomaly Detection (UEBA): Detecting Risky Users from Logon Logs



A behavior-based detection tool that learns each user's normal logon behavior and flags deviations, built with Python, pandas and scikit-learn.



\## Goal

Detect compromised or malicious accounts without relying on known attack signatures.



\## Data

Synthetic logon logs: 50 users, 45 hosts (5 servers), 30 days. Four attackers were injected during days 25 to 30:



| User | Injected behavior | MITRE ATT\&CK |

|---|---|---|

| user07 | Logons to 12 hosts in a day | T1021 Remote Services |

| user21 | Logons at 1-4 AM | T1078 Valid Accounts |

| user33 | 40 failed logons in a burst | T1110 Brute Force |

| user45 | Servers never used before | T1078 / T1021 |



\## Method

1\. Features per user per day: logons, failures, distinct hosts, server logons, off-hours logons

2\. Baseline from days 1-24 only, so attacker activity never contaminates "normal"

3\. Per-user z-scores and rare-event rules

4\. Isolation Forest trained only on baseline days

5\. Final score = weighted mix of rules and model, with a "why flagged" explanation



\## Results

\- Attackers in top 4 with 50/50 weights: 2/4

\- Attackers in top 4 with 70/30 weights (rules weighted higher): 4/4

\- Attackers in top 10: 4/4

\- False positives in top 10: 6 normal users with unusually busy days



!\[Radial chart](output/top\_risky\_users\_radial.png)



\## Limitations

\- Data is synthetic, so real logs will be noisier

\- The Isolation Forest could not see offhours and server\_logons, because they were always 0 in the baseline

\- The flag threshold (final >= 5) is arbitrary

\- Anomalous does not mean malicious

\- A baseline that already contains an attacker hides them



\## Run it

```

pip install pandas numpy scikit-learn matplotlib

python scripts/generate\_logs.py

python scripts/features.py

python scripts/score\_rules.py

python scripts/iforest.py

python scripts/report.py

python scripts/chart\_radial.py

```

