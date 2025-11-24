import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

DIR_OUTPUT = "../out/"
CSV_FILE = DIR_OUTPUT + "conc.csv"
OUTPUT_FILE = DIR_OUTPUT + "conc.png"

def plot_conc():
    # Lecture du CSV
    df = pd.read_csv(CSV_FILE)

    # Garder seulement les runs valides
    df = df[df["FAILED"] == 0]

    # Convertir ms → secondes
    df["AVG_TIME"] = df["AVG_TIME"] / 1000.0

    # Moyenne + écart-type par niveau de concurrence
    grouped = df.groupby("PARAM")["AVG_TIME"].agg(["mean", "std"]).reset_index()

    # Positions régulières pour le plot
    positions = np.arange(len(grouped))
    means = grouped["mean"]
    stds = grouped["std"]
    labels = grouped["PARAM"]

    plt.figure(figsize=(12, 6))

    plt.bar(positions, means, yerr=stds, capsize=5, width=0.6)

    plt.xticks(positions, labels)  # labels = 1,10,20,50,100,1000

    plt.xlabel("Utilisateurs concurrents")
    plt.ylabel("Temps moyen par requête (secondes)")
    plt.title("Temps moyen par requête selon la concurrence")

    plt.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(OUTPUT_FILE)
    plt.close()

    print(f"Graphique créé : {OUTPUT_FILE}")

def main():
    print("== Plot Concurrency Results ==\n")
    plot_conc()
    
if __name__ == "__main__":
    main()
