#!/usr/bin/env python3
import requests
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


# ---------------- Configuration ----------------

APP_URL = "https://tinyinsta-benchmark-479218.ew.r.appspot.com"
ENDPOINT = APP_URL + "/api/timeline"
USERS_PREFIX = "load"
LIMIT = 20
FOLLOWERS_PER_USER_VALUES = [10,50,100]
RUN_NUMBER = 3
CONCURRENCY = 50
RUNS = 3
USERS = 1000


CSV_RAW = "../out/fanout_raw.csv"
CSV_SUMMARY = "../out/fanout_summary.csv"

## python seed.py --users 1000 --posts 100 --follows-min 10 --follows-max 10
## python seed.py --users 1000 --posts 100 --follows-min 50 --follows-max 50
## python seed.py --users 1000 --posts 100 --follows-min 100  --follows-max 100

def fetch_timeline(username: str):
    start = time.time()

    try:
        r = requests.get(ENDPOINT, params={"user": username, "limit": LIMIT})
        end = time.time()
        duration = end - start

        if duration <= 0:
            return username, start, end, None, True

        if r.status_code != 200:
            return username, start, end, duration, True

        return username, start, end, duration, False

    except Exception:
        end = time.time()
        return username, start, end, None, True


def run_fanout_test(concurrency: int, run: int, raw_writer):

    usernames = [f"{USERS_PREFIX}{i}" for i in range(1, concurrency + 1)]

    durations_valid = []
    failed_global = False

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(fetch_timeline, user) for user in usernames]

        for f in as_completed(futures):
            user, start, end, duration, failed = f.result()

            # brut results
            raw_writer.writerow([
                FOLLOWERS_PER_USER_VALUES[RUN_NUMBER - 1],
                run,
                user,
                f"{start:.6f}",
                f"{end:.6f}",
                "" if duration is None else f"{duration:.6f}",
                int(failed)
            ])

            # si une requête échoue → FAILED=1
            if failed or duration is None:
                failed_global = True
            else:
                durations_valid.append(duration)

    # moyenne sur les requêtes réussies
    if durations_valid:
        avg_time = sum(durations_valid) / len(durations_valid)
    else:
        avg_time = None 

    return avg_time, failed_global



# ---------------- Main: Expérience Fanout ----------------

def main():
    print("== Benchmark Posts ==\n")

    with open(CSV_RAW, "a", newline="") as raw_file, \
         open(CSV_SUMMARY, "a", newline="") as sum_file:

        raw_writer = csv.writer(raw_file)
        sum_writer = csv.writer(sum_file)

        raw_writer.writerow(["PARAM", "RUN", "USER", "START", "END", "DURATION", "FAILED"])
        sum_writer.writerow(["PARAM", "RUN", "AVG_TIME", "FAILED"])
        
        for run in range(1, RUNS + 1):
            
            print(f"Run {run}... ", end="", flush=True)

            avg_time, failed = run_fanout_test(CONCURRENCY, run, raw_writer)

            sum_writer.writerow([
                    FOLLOWERS_PER_USER_VALUES[RUN_NUMBER - 1],
                    run,
                    f"{avg_time:.3f}" if avg_time else "",
                    int(failed)
                ])

            if avg_time:
                print(f"{avg_time:.4f} s")
            else:
                print("FAILED")

    print("\nBenchmark terminé.")
    print(f"  → Données brutes : {CSV_RAW}")
    print(f"  → Résumé : {CSV_SUMMARY}")


if __name__ == "__main__":
    main()