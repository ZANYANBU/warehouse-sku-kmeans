"""Draw the deck's graphs as pictures, so they show in every viewer (a preview pane skips chart objects)."""
import json, sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
G = json.load(open(HERE / "graphs.json"))
ELBOW = [1532.0, 1025.2, 772.5, 600.1, 511.0, 453.9, 412.4, 368.2]

TEAL, SLATE, GRID, INK = "#0F4C5C", "#5F7180", "#E3EBEE", "#16212B"
BLUE, AMBER, PINK, GREEN, PALE, ORANGE = "#2A78D6", "#EDA100", "#E87BA4", "#008300", "#9BBBE4", "#F28C28"
ZC = {"A": BLUE, "B": AMBER, "C": PINK, "D": GREEN}
plt.rcParams.update({"font.family": "Arial", "font.size": 11, "axes.edgecolor": "#C9D3D8", "axes.labelcolor": SLATE,
                     "xtick.color": SLATE, "ytick.color": SLATE, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlecolor": TEAL, "axes.titlesize": 12.5, "axes.titleweight": "bold"})


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, facecolor="white")
    plt.close(fig)
    print("drew", name)


def frame(ax, axis="y"):
    ax.grid(axis=axis, color=GRID, linewidth=0.9); ax.set_axisbelow(True)


# Orders in each month
fig, ax = plt.subplots(figsize=(9.0, 2.6))
ax.bar(G["months_all"], G["orders_all"], color=BLUE, width=0.7)
ax.set_title("Orders placed in each month"); frame(ax)
ax.set_yticks(range(0, 8001, 2000)); ax.set_yticklabels([f"{v:,}" for v in range(0, 8001, 2000)])
ax.tick_params(axis="x", labelrotation=60, labelsize=9)
for label in ax.get_xticklabels(): label.set_ha("right")
fig.tight_layout(); save(fig, "orders_by_month.png")

# Elbow curve
fig, ax = plt.subplots(figsize=(5.2, 3.55))
ks = list(range(1, 9))
ax.plot(ks, ELBOW, color=ORANGE, linewidth=3, marker="o", markersize=8)
ax.scatter([4], [ELBOW[3]], s=330, facecolors="none", edgecolors=INK, linewidths=2, zorder=3)
ax.annotate("k = 4", (4, ELBOW[3]), textcoords="offset points", xytext=(14, 12), fontweight="bold", color=INK)
ax.set_title("Elbow curve on the real data (383 SKUs)"); ax.set_xlabel("Number of clusters (k)"); ax.set_ylabel("Within-cluster variance")
ax.set_ylim(0, 1700); frame(ax)
fig.tight_layout(); save(fig, "elbow.png")

# Silhouette score
fig, ax = plt.subplots(figsize=(5.2, 3.55))
sk = list(G["silhouette"]); sv = [G["silhouette"][k] for k in sk]
bars = ax.bar(sk, sv, color=[AMBER if k == "4" else PALE for k in sk], width=0.66)
for bar, v in zip(bars, sv):
    ax.text(bar.get_x() + bar.get_width() / 2, v + 0.008, f"{v:.2f}", ha="center", va="bottom", color=INK, fontsize=11)
ax.set_title("Silhouette score for each k (real data)"); ax.set_xlabel("Number of clusters (k)"); ax.set_ylim(0, 0.45); frame(ax)
fig.tight_layout(); save(fig, "silhouette.png")

# What each cluster looks like: four small graphs
panels = [("Average orders", [160, 52, 48, 45], "{:.0f}"), ("Season index", [2.6, 3.5, 7.4, 3.2], "{:.1f}"),
          ("Average volume (L)", [9.2, 47.1, 12.9, 5.1], "{:.1f}"), ("Average weight (kg)", [1.1, 7.6, 1.1, 0.6], "{:.1f}")]
fig, axes_ = plt.subplots(1, 4, figsize=(9.0, 2.75))
for ax, (title, values, fmt) in zip(axes_, panels):
    bars = ax.bar(list("ABCD"), values, color=[ZC[z] for z in "ABCD"], width=0.66)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + max(values) * 0.02, fmt.format(v), ha="center", va="bottom", color=INK, fontsize=11)
    ax.set_title(title); ax.set_yticks([]); ax.spines["left"].set_visible(False); ax.set_ylim(0, max(values) * 1.18)
    ax.tick_params(axis="x", labelsize=12, colors=INK)
fig.tight_layout(); save(fig, "cluster_averages.png")

# A seasonal SKU against a fast mover
fig, ax = plt.subplots(figsize=(6.0, 3.55))
ax.plot(G["months"], G["fast"], color=BLUE, linewidth=3, marker="o", markersize=6, label="Fast mover (527 orders)")
ax.plot(G["months"], G["seasonal"], color=PINK, linewidth=3, marker="o", markersize=6, label="Seasonal SKU (114 orders)")
ax.set_title("Orders in each month, two real SKUs"); ax.set_ylim(0, 140); frame(ax)
ax.tick_params(axis="x", labelrotation=60, labelsize=9)
for label in ax.get_xticklabels(): label.set_ha("right")
ax.legend(frameon=False, loc="upper left", fontsize=10.5, labelcolor=INK)
fig.tight_layout(); save(fig, "seasonal_fast.png")

# Walk per pick in the model
fig, ax = plt.subplots(figsize=(5.9, 1.95))
names, values = ["K-Means zones", "No grouping"], [46.5, 63.8]
bars = ax.barh(names, values, color=[GREEN, PALE], height=0.6)
for bar, v in zip(bars, values):
    ax.text(v + 1.2, bar.get_y() + bar.get_height() / 2, f"{v:.1f} m", va="center", fontweight="bold", color=INK, fontsize=12)
ax.set_title("Walk per pick in the model (metres)"); ax.set_xlim(0, 80); frame(ax, "x")
ax.tick_params(axis="y", labelsize=11.5, colors=INK)
fig.tight_layout(); save(fig, "walk_per_pick.png")
