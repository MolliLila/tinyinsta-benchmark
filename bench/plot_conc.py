import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

DIR_OUTPUT = "../out/"
CSV_FILE = os.path.join(DIR_OUTPUT, "conc.csv")
OUTPUT_FILE = os.path.join(DIR_OUTPUT, "conc.png")

def plot_conc(show=False):
    if not os.path.exists(CSV_FILE):
        print(f"Fichier introuvable : {CSV_FILE}")
        return

    # Lecture du CSV
    df = pd.read_csv(CSV_FILE)

    # Filtrer les runs valides
    df = df[df["FAILED"] == 0]

    # Calcul des moyennes et écarts-types
    grouped = df.groupby("PARAM")["AVG_TIME"].agg(["mean", "std"]).reset_index()
    grouped = grouped.sort_values("PARAM")

    positions = np.arange(len(grouped))
    means = grouped["mean"]
    stds = grouped["std"]
    labels = grouped["PARAM"]

    plt.style.use("seaborn-v0_8-deep")
    plt.figure(figsize=(12, 6))
    plt.bar(positions, means, yerr=stds, capsize=5, width=0.6, color="#4C72B0")

    plt.xticks(positions, labels)
    plt.xlabel("Utilisateurs concurrents")
    plt.ylabel("Temps moyen par requête (secondes)")
    plt.title("Temps moyen par requête selon la concurrence")
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    # Ajouter les valeurs sur les barres
    for i, v in enumerate(means):
        plt.text(i, v + stds.iloc[i] + 0.02 * v, f"{v:.2f}", ha='center', fontsize=9)

    plt.tight_layout()

    if show:
        plt.show()
    else:
        plt.savefig(OUTPUT_FILE)
        print(f"Graphique créé : {OUTPUT_FILE}")

def main():
    print("== Plot Concurrency Results ==\n")
    plot_conc()

if __name__ == "__main__":
    main()
