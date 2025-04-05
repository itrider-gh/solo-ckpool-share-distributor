# solo-ckpool-share-distributor

This tool calculates the reward distribution between mining workers when using [`ckpool`](https://bitcointalk.org/index.php?topic=790323.0) in **solo mode** (`-B`) with **share logging enabled** (`-L`).  
It is designed for scenarios where all workers mine on the same Bitcoin address (solo mining), but you still want to split the reward proportionally based on their contributed work.

---

## ✅ Usage Context

This is intended for **solo mining setups** where:
- All workers mine using the **same Bitcoin address**
- You're running `ckpool` with the following options:

```bash
./ckpool -B -L -c ckpool.conf
```

- `-B`: Solo mining mode (all rewards go to a single address)
- `-L`: Enables share logging in `logs/{round}/*.sharelog`

---

## ⚙️ How It Works

The script:
1. Scans `.sharelog` files from the last **X days** (default: 14)
2. Filters shares submitted by the configured **Bitcoin address**
3. Groups contributions by `workername`
4. Computes per-worker:
   - Total number of valid shares
   - Average vardiff
   - Weighted contribution (`shares × avg vardiff`)
   - Proportional percentage of the total work

---

## 🚀 Run

```bash
python3 repartition.py \
  --logs /path/to/ckpool/logs \
  --output /path/to/repartition.json \
  --username YOUR_SOLO_BTC_ADDRESS
```

Optional arguments:
- `--days 14`: Number of days to look back for sharelogs (default: 14)

---

## 📦 Output

The output is a JSON file with one entry per worker:

```json
{
  "workerA": {
    "shares": 1024,
    "avg_vardiff": 512.0,
    "weight": 524288.0,
    "percentage": 45.8
  },
  ...
}
```

---

## 🔁 Tip: Automation

To update the repartition every 10 minutes:

```cron
*/10 * * * * /usr/bin/python3 /path/to/repartition.py --username YOUR_BTC_ADDR >> /path/to/repartition.log 2>&1
```

Make sure the cron user has permission to access the ckpool logs.
