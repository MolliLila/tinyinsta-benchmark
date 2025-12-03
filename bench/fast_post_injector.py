#!/usr/bin/env python3
import requests
import random
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from tqdm import tqdm

BASE = "https://tinyinsta-benchmark-479218.ew.r.appspot.com"
LOGIN_URL = BASE + "/login"
POST_URL  = BASE + "/post"

USERS = 1000
THREADS = 50
TOTAL_POSTS = 1_000_000


progress_lock = Lock()

def create_session(username):
    """Crée une session Flask authentifiée comme un vrai user."""
    s = requests.Session()
    r = s.post(LOGIN_URL, data={"username": username}, timeout=5)
    if r.status_code not in (200, 302):
        raise RuntimeError(f"Login failed for {username}")
    return s

def worker(thread_id, usernames, posts_per_thread, pbar):
    """Génère plusieurs posts en étant connecté comme un vrai utilisateur."""
    username = random.choice(usernames)
    session = create_session(username)

    ok = 0
    for i in range(posts_per_thread):
        try:
            r = session.post(POST_URL, data={"content": f"Mass post {thread_id}-{i}"}, timeout=3)
            if r.status_code in (200, 302):
                ok += 1
        except:
            pass

        # mettre à jour la barre de progression
        with progress_lock:
            pbar.update(1)

    return ok

def main():
    usernames = [f"load{i}" for i in range(1, USERS + 1)]
    posts_per_thread = TOTAL_POSTS // THREADS

    print(f"➡ Injection massive : {TOTAL_POSTS:,} posts")
    print(f"➡ Threads : {THREADS}")
    print("-----------------------------------------------------")

    start = time.time()

    # Barre de progression globale
    pbar = tqdm(total=TOTAL_POSTS, smoothing=0.1)

    total_ok = 0
    with ThreadPoolExecutor(max_workers=THREADS) as ex:
        futures = [
            ex.submit(worker, t, usernames, posts_per_thread, pbar)
            for t in range(THREADS)
        ]

        for f in futures:
            total_ok += f.result()

    pbar.close()
    end = time.time()

    print("-----------------------------------------------------")
    print(f" Total OK : {total_ok:,}")
    print(f" Temps total : {end - start:.1f} sec ({(end-start)/60:.1f} min)")
    print(f" Débit moyen : {TOTAL_POSTS / (end - start):.1f} posts/sec")
    print("-----------------------------------------------------")

if __name__ == "__main__":
    main()
