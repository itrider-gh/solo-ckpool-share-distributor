# solo-ckpool-share-distributor

This tool calculates the reward distribution between mining workers when using [`ckpool`](https://bitcointalk.org/index.php?topic=790323.0) in **solo mode** (`-B`) with **share logging enabled** (`-L`).  
It is designed for scenarios where all workers mine on the same Bitcoin address (solo mining), but you still want to split the reward proportionally based on their contributed work.

---

## ✅ Usage Context

This is for **solo mining** setups where:
- All workers mine using the **same Bitcoin address**
- You're running `ckpool` with the following options:
  ```bash
  ./ckpool -B -L -c ckpool.conf

  - `-B` = Solo mining mode (1 address per block reward)
  - `-L` = Enable share logging in `logs/{round}/*.sharelog`

---

## ⚙️ How It Works

The script:
1. Scans the latest 200 `.sharelog` files (~14 days of blocks)
2. Filters only shares submitted by the configured Bitcoin address
3. Groups them by `workername`
4. Computes:
   - Number of valid shares
   - Average vardiff
   - Weighted contribution (`shares × avg vardiff`)
   - Proportional percentage of the total work

---

## 🚀 Run

```bash
python3 repartition.py \
  --logs /path/to/logs \
  --output /path/to/repartition.json \
  --username YOUR_SOLO_BTC_ADDRESS
```

---

## 📦 Output

A JSON file with one entry per worker:

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

To update the repartition automatically:
```cron
*/10 * * * * /usr/bin/python3 /path/to/repartition.py --username YOUR_BTC_ADDR >> /path/to/log.log 2>&1
```
