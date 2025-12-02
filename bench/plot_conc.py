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

 # Charger CSV
df = pd.read_csv(CSV_FILE)

# Convertir AVG_TIME
df["AVG_TIME"] = pd.to_numeric(df["AVG_TIME"], errors="coerce")

# Groupes moyennes
grouped = df.groupby("PARAM")["AVG_TIME"].mean().reset_index()

# Failed flag par PARAM (si au moins un run échoue)
failed_flag = df.groupby("PARAM")["FAILED"].max()

# Tri
grouped = grouped.sort_values("PARAM")

positions = np.arange(len(grouped))
means = grouped["AVG_TIME"]
labels = grouped["PARAM"]

# Couleurs : bleu si OK, rouge si échec
colors = [
    "#4C72B0" if failed_flag[param] == 0 else "#D9534F" 
    for param in grouped["PARAM"]
]

plt.figure(figsize=(12, 6))
plt.bar(positions, means, width=0.6, color=colors)

plt.xticks(positions, labels)
plt.xlabel("Utilisateurs concurrents")
plt.ylabel("Temps moyen (s)")
plt.title("Temps moyen selon la concurrence")

for i, v in enumerate(means):
    plt.text(i, v + 0.01 * v, f"{v:.3f}", ha='center', fontsize=9)

plt.tight_layout()
plt.savefig(OUTPUT_FILE)


def main():
    print("== Plot Concurrency Results ==\n")
    plot_conc()

if __name__ == "__main__":
    main()
