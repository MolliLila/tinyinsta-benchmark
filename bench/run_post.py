#!/usr/bin/env python3
import requests
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.cloud import datastore


# ---------------- Configuration ----------------

APP_URL = "https://tinyinsta-benchmark-479218.ew.r.appspot.com"
SEED_TOKEN = "change-me-seed-token"

USERS = 1000
PREFIX = "load"
FOLLOWERS = 20
CONCURRENCY = 50
RUNS = 3

POSTS_PER_USER_VALUES = [10, 100, 1000]

CSV_FILE = "../out/post.csv"


# ---------------- Utility: Clear posts ----------------

def clear_posts():
    print(" Suppression des Posts...")
    client = datastore.Client()
    query = client.query(kind="Post")

    count = 0
    batch = []

    for entity in query.fetch():
        batch.append(entity.key)
        count += 1

        if len(batch) >= 500:
            client.delete_multi(batch)
            batch = []

    if batch:
        client.delete_multi(batch)

    print(f" Posts supprimés : {count}")


# ---------------- Utility: Seed posts ----------------

def seed_posts(total_posts):
    print(f" Seed de {total_posts} posts...")

    url = f"{APP_URL}/admin/seed"

    # On divise en batches pour éviter les timeouts
    BATCH = 100
    remaining = total_posts

    while remaining > 0:
        posts = min(BATCH, remaining)
        remaining -= posts

        params = {
            "users": USERS,
            "posts": posts,
            "prefix": PREFIX,
            "follows_min": 0,
            "follows_max": 0
        }

        resp = requests.post(
            url,
            headers={"X-Seed-Token": SEED_TOKEN},
            params=params
        )

        if resp.status_code != 200:
            print(" Seed failed:", resp.text)
            return False

        print(f"   Batch seed : {posts} posts")

    print(" Seed terminé.\n")
    return True


# ---------------- Benchmark ----------------

def fetch_timeline(username):
    try:
        start = time.perf_counter()
        r = requests.get(f"{APP_URL}/api/timeline?user={username}&limit=20", timeout=10)
        latency = (time.perf_counter() - start) * 1000

        if r.status_code != 200 or latency <= 0:
            return None, True

        return latency, False
    except:
        return None, True


def run_benchmark():
    usernames = [f"{PREFIX}1"] * CONCURRENCY
    latencies = []
    failed = False

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as exe:
        futures = [exe.submit(fetch_timeline, u) for u in usernames]

        for f in as_completed(futures):
            latency, error = f.result()
            if error or latency is None:
                failed = True
            else:
                latencies.append(latency)

    if latencies:
        avg = sum(latencies) / len(latencies)
    else:
        avg = None
        failed = True

    return avg, failed


# ---------------- Main: Expérience Posts ----------------

def main():
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["PARAM", "AVG_TIME", "RUN", "FAILED"])

        for posts_per_user in POSTS_PER_USER_VALUES:
            total_posts = posts_per_user * USERS

            print(f"==============================")
            print(f" TEST : {posts_per_user} posts/user → {total_posts} posts")
            print(f"=============================")

            # 1) Clear posts
            clear_posts()

            # 2) Seed new number of posts
            ok = seed_posts(total_posts)
            if not ok:
                print(" Impossible de seed. On passe au prochain test.")
                continue

            # 3) Bench 3 runs
            for run in range(1, RUNS + 1):
                print(f"  Run {run}...")
                avg, failed = run_benchmark()

                if failed or avg is None:
                    writer.writerow([posts_per_user, "", run, 1])
                    print("   → FAILED")
                else:
                    writer.writerow([posts_per_user, f"{avg:.2f}", run, 0])
                    print(f"   → {avg:.2f} ms")

    print("\n Benchmark terminé. Résultats écrits dans post.csv")


if __name__ == "__main__":
    main()
