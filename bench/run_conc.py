#!/usr/bin/env python3
import requests
import time
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

APP_URL = "https://tinyinsta-benchmark-479218.ew.r.appspot.com"
ENDPOINT = APP_URL + "/api/timeline"
USERS_PREFIX = "load"
LIMIT = 20

CONCURRENCES = [1, 10, 20, 50, 100, 1000]
RUNS = 3
CSV_FILE = "../out/conc.csv"


def fetch_timeline(username: str):
    try:
        start = time.perf_counter()  
        r = requests.get(
            ENDPOINT,
            params={"user": username, "limit": LIMIT}
        )
        latency_ms = (time.perf_counter() - start) * 1000

        # Latence impossible
        if latency_ms <= 0:
            return None, True

        if r.status_code != 200:
            return latency_ms, True 

        return latency_ms, False

    except Exception:
        return latency_ms, True 


def run_concurrency_test(concurrency: int):
    usernames = [f"{USERS_PREFIX}{i}" for i in range(1, concurrency + 1)]
    latencies = []
    failed = False

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(fetch_timeline, user) for user in usernames]

        for f in as_completed(futures):
            latency, error = f.result()
            if error or latency is None:
                failed = True
            else:
                latencies.append(latency)

    if latencies:
        avg_time = sum(latencies) / len(latencies)
    else:
        avg_time = None
        failed = True

    return avg_time, failed


def main():
    print("== Benchmark Concurrence ==\n")
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["PARAM", "AVG_TIME", "RUN", "FAILED"])

        for concurrency in CONCURRENCES:
            print(f"\n### Testing concurrency = {concurrency}")

            for run in range(1, RUNS + 1):
                print(f"Run {run}... ", end="", flush=True)

                avg_time, failed = run_concurrency_test(concurrency)

                if failed or avg_time is None:
                    writer.writerow([concurrency, "", run, 1])
                    print("FAILED")
                else:
                    writer.writerow([concurrency, f"{avg_time:.2f}", run, 0])
                    print(f"{avg_time:.2f} ms")

    print("\nBenchmark terminé. Résultats dans conc.csv")


if __name__ == "__main__":
    main()
