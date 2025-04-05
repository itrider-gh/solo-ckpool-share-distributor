import json
import os
import re
import argparse
import time
from collections import defaultdict

# === ARGUMENTS ===
parser = argparse.ArgumentParser(description="Distribute solo ckpool rewards per worker based on vardiff and share count.")
parser.add_argument("--logs", type=str, default="./logs", help="Path to ckpool logs directory (default: ./logs)")
parser.add_argument("--output", type=str, default="./repartition.json", help="Path to output JSON file (default: ./repartition.json)")
parser.add_argument("--username", type=str, required=True, help="Solo Bitcoin address used by all workers (required)")
parser.add_argument("--days", type=int, default=14, help="Number of days to look back for rounds (default: 14)")

args = parser.parse_args()
base_dir = args.logs
output_file = args.output
solo_username = args.username
cutoff_seconds = args.days * 24 * 3600  # Convert days to seconds

# === INITIALIZATION ===
total_vardiff_per_worker = defaultdict(float)
share_count_per_worker = defaultdict(int)

now = time.time()

# === SCAN ROUND FOLDERS MODIFIED IN LAST N DAYS ===
round_dirs = sorted([
    d for d in os.listdir(base_dir)
    if (
        os.path.isdir(os.path.join(base_dir, d))
        and re.fullmatch(r"[0-9a-f]{8}", d)
        and now - os.path.getmtime(os.path.join(base_dir, d)) <= cutoff_seconds
    )
], reverse=True)

print(f"📁 Found {len(round_dirs)} round directories modified in the last {args.days} days")

# === PARSE SHARELOG FILES ===
for round_dir in round_dirs:
    round_path = os.path.join(base_dir, round_dir)
    for filename in os.listdir(round_path):
        if filename.endswith(".sharelog"):
            filepath = os.path.join(round_path, filename)
            try:
                with open(filepath, "r") as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            if data.get("result") is True and data.get("username") == solo_username:
                                workername = data.get("workername", "unknown")
                                vardiff = float(data.get("diff", 0))
                                total_vardiff_per_worker[workername] += vardiff
                                share_count_per_worker[workername] += 1
                        except json.JSONDecodeError:
                            continue
            except (FileNotFoundError, PermissionError):
                continue

# === COMPUTE WEIGHTS PER WORKER ===
worker_weights = {}
for worker in share_count_per_worker:
    avg_vardiff = total_vardiff_per_worker[worker] / share_count_per_worker[worker]
    weight = share_count_per_worker[worker] * avg_vardiff
    worker_weights[worker] = {
        "shares": share_count_per_worker[worker],
        "avg_vardiff": avg_vardiff,
        "weight": weight
    }

# === COMPUTE PERCENTAGES ===
total_weight = sum(w["weight"] for w in worker_weights.values())
for worker in worker_weights:
    worker_weights[worker]["percentage"] = (
        (worker_weights[worker]["weight"] / total_weight) * 100
        if total_weight > 0 else 0
    )

# === SAVE FINAL JSON ===
with open(output_file, "w") as f:
    json.dump(worker_weights, f, indent=2)

print(f"✅ Share-based reward distribution saved to: {output_file}")
