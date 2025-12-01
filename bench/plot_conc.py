import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

DIR_OUTPUT = "../out/"
CSV_FILE = os.path.join(DIR_OUTPUT, "conc_summary.csv")
OUTPUT_FILE = os.path.join(DIR_OUTPUT, "conc.png")

def plot_conc(show=False):
    if not os.path.exists(CSV_FILE):
        print(f"Fichier introuvable : {CSV_FILE}")
        return

    # Lecture du CSV
    df = pd.read_csv(CSV_FILE)

   
    
    # Convertir AVG_TIME en float
    df["AVG_TIME"] = pd.to_numeric(df["AVG_TIME"], errors="coerce")

    # Filtrer les runs valides
    df = df[df["FAILED"] == 0]
        
    # Retirer AVG_TIME manquants
    df = df.dropna(subset=["AVG_TIME"])

    # Convertir PARAM en numérique
    df["PARAM"] = pd.to_numeric(df["PARAM"], errors="coerce")

    # Calcul de la moyenne seulement
    grouped = df.groupby("PARAM")["AVG_TIME"].mean().reset_index()
    grouped = grouped.sort_values("PARAM")

    positions = np.arange(len(grouped))
    means = grouped["AVG_TIME"]
    labels = grouped["PARAM"]

    plt.style.use("seaborn-v0_8-deep")
    plt.figure(figsize=(12, 6))

    # Barres SANS écart-type
    plt.bar(positions, means, width=0.6, color="#4C72B0")

    plt.xticks(positions, labels)
    plt.xlabel("Utilisateurs concurrents")
    plt.ylabel("Temps moyen par requête (secondes)")
    plt.title("Temps moyen par requête selon la concurrence")
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    
    # Ajouter la moyenne au-dessus des barres
    for i, v in enumerate(means):
        plt.text(i, v + 0.01 * v, f"{v:.3f}", ha='center', fontsize=9)

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
