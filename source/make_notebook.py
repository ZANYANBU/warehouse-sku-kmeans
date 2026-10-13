"""Write the Colab notebook, and the same code as one plain script for checking it runs."""
import json, sys

OUT_NB, OUT_PY = sys.argv[1], sys.argv[2]

CELLS = [
("md", """# Grouping warehouse products with K-Means clustering

Machine Learning (21CSC305P), Project Review 3, Team Cash guard.

This notebook reads a **real, public dataset straight from the internet**, builds four numbers for every product (SKU), groups the SKUs with **K-Means**, and gives each group a place in the warehouse. It draws a graph at every step.

**Data:** the Brazilian e-commerce dataset published by Olist: about 99,000 orders placed between 2016 and 2018 (MIT licence).

- Open the data in a browser: https://github.com/olist/work-at-olist-data/tree/master/datasets
- The notebook reads the four CSV files from that folder. Their full addresses are printed by the first cell.

Run every cell from top to bottom: **Runtime > Run all**."""),

("md", """## 1. Read the data from the live link"""),
("code", """import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter, ScalarFormatter
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

# The folder to open in a browser:
FOLDER = "https://github.com/olist/work-at-olist-data/tree/master/datasets"
# Where the files themselves are read from. This address is not a page on its own:
# a file name has to follow it.
RAW = "https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets/"
FILES = {
    "products": "olist_products_dataset.csv",              # size and weight of every product
    "items": "olist_order_items_dataset.csv",              # one row each time a product was ordered
    "orders": "olist_orders_dataset.csv",                  # when each order was placed
    "names": "product_category_name_translation.csv",      # category names in English
}
for file in FILES.values():
    print("reading", RAW + file)

products = pd.read_csv(RAW + FILES["products"])
items = pd.read_csv(RAW + FILES["items"])
orders = pd.read_csv(RAW + FILES["orders"], parse_dates=["order_purchase_timestamp"])
names = pd.read_csv(RAW + FILES["names"])

def plain_log(axis):
    # A log axis with ordinary numbers on it (10, 100) and no crowd of small labels.
    axis.set_major_formatter(ScalarFormatter()); axis.set_minor_formatter(NullFormatter())

print()
print(f"{len(orders):,} orders, {len(items):,} order lines, {items['product_id'].nunique():,} products")
print("from", orders["order_purchase_timestamp"].min().date(), "to", orders["order_purchase_timestamp"].max().date())"""),

("md", """### Graph 1: orders in each month

The whole dataset at a glance. Orders grow through 2017, and November 2017 (Black Friday) stands out."""),
("code", """by_month = orders["order_purchase_timestamp"].dt.to_period("M").value_counts().sort_index()
by_month = by_month[by_month > 100]                      # drop the few stray months at both ends
plt.figure(figsize=(11, 3.6))
plt.bar(by_month.index.astype(str), by_month.values, color="#2a78d6")
plt.xticks(rotation=60, ha="right"); plt.ylabel("Orders"); plt.title("Orders placed in each month")
plt.grid(axis="y", alpha=0.3); plt.tight_layout(); plt.show()"""),

("md", """## 2. Four numbers for every SKU

| Number | What it means | Where it comes from |
|---|---|---|
| `picks` | Pick frequency: how many times the product was ordered | count of order lines |
| `season` | Seasonal demand: share of its orders in its busiest month, times 12. 1 means the same every month; 12 means everything in one month | order dates |
| `volume` | Physical size in litres | length x height x width |
| `weight` | Handling: weight in kg | product weight |

Only products ordered **at least 30 times** are kept, so that the seasonal number is not decided by two or three orders."""),
("code", """lines = items.merge(orders[["order_id", "order_purchase_timestamp"]], on="order_id")
lines["month"] = lines["order_purchase_timestamp"].dt.month

picks = lines.groupby("product_id").size().rename("picks")
busiest = lines.groupby(["product_id", "month"]).size().groupby("product_id").max().rename("busiest_month")

sku = products.merge(picks, on="product_id").merge(busiest, on="product_id")
sku["season"] = sku["busiest_month"] * 12 / sku["picks"]
sku["volume"] = sku["product_length_cm"] * sku["product_height_cm"] * sku["product_width_cm"] / 1000
sku["weight"] = sku["product_weight_g"] / 1000
sku = sku.merge(names, on="product_category_name", how="left")
sku["category"] = sku["product_category_name_english"].fillna(sku["product_category_name"]).fillna("unknown")

sku = sku[sku["picks"] >= 30].dropna(subset=["volume", "weight"]).reset_index(drop=True)
FEATURES = ["picks", "season", "volume", "weight"]
LABELS = {"picks": "Picks (order lines)", "season": "Season index", "volume": "Volume (litres)", "weight": "Weight (kg)"}
print(len(sku), "SKUs with at least 30 order lines")
sku[["product_id", "category"] + FEATURES].round(2).head(8)"""),

("md", """## 3. Scale the numbers

K-Means measures distance, so a big number would decide everything. Two steps fix that:

1. `picks`, `volume` and `weight` are very uneven (a few huge values), so we take their **log**.
2. Every column is brought to the **same scale** (mean 0, spread 1)."""),
("code", """X = sku[FEATURES].copy()
for col in ["picks", "volume", "weight"]:
    X[col] = np.log1p(X[col])
X = StandardScaler().fit_transform(X)
print("shape of the scaled data:", X.shape)"""),

("md", """### Graph 2: the four numbers before and after scaling

Top row: the raw numbers. Most SKUs are small, and a few are huge. Bottom row: after the log and the scaling, every column sits on the same scale."""),
("code", """fig, axes = plt.subplots(2, 4, figsize=(14, 5.5))
for i, col in enumerate(FEATURES):
    axes[0, i].hist(sku[col], bins=30, color="#2a78d6")
    axes[0, i].set_title(LABELS[col] + ": raw")
    axes[1, i].hist(X[:, i], bins=30, color="#eda100")
    axes[1, i].set_title(LABELS[col] + ": scaled")
axes[0, 0].set_ylabel("Number of SKUs"); axes[1, 0].set_ylabel("Number of SKUs")
plt.tight_layout(); plt.show()"""),

("md", """## 4. Choose k with the elbow method

Run K-Means for k = 1 to 8 and plot the error (within-cluster variance). Pick the k where the curve bends.
The silhouette score is a second check: higher means the groups are better separated."""),
("code", """ks = list(range(1, 9))
errors, silhouettes = [], {}
for k in ks:
    model = KMeans(n_clusters=k, n_init=20, random_state=42).fit(X)
    errors.append(model.inertia_)
    if k > 1:
        silhouettes[k] = silhouette_score(X, model.labels_)

for k in ks:
    drop = "" if k == 1 else f"  {100 * (1 - errors[k - 1] / errors[k - 2]):.0f}% lower than k = {k - 1}"
    score = "" if k == 1 else f"  silhouette {silhouettes[k]:.3f}"
    print(f"k = {k}: error {errors[k - 1]:7.1f}{drop}{score}")"""),

("md", """### Graph 3: the elbow curve and the silhouette score

Left: the error bends at k = 4. Right: the silhouette score is also highest at k = 4."""),
("code", """K = 4
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].plot(ks, errors, marker="o", color="#2a78d6")
axes[0].scatter([K], [errors[K - 1]], s=260, facecolors="none", edgecolors="black", linewidths=2, zorder=3)
axes[0].annotate(f"k = {K}", (K, errors[K - 1]), textcoords="offset points", xytext=(14, 12), fontweight="bold")
axes[0].set_xlabel("Number of clusters (k)"); axes[0].set_ylabel("Within-cluster variance"); axes[0].set_title("Elbow curve")
axes[0].grid(alpha=0.3)
sil_k = list(silhouettes)
axes[1].bar(sil_k, [silhouettes[k] for k in sil_k], color=["#eda100" if k == K else "#9bbbe4" for k in sil_k])
axes[1].set_xlabel("Number of clusters (k)"); axes[1].set_ylabel("Silhouette score"); axes[1].set_title("Silhouette score (higher is better)")
axes[1].grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.show()"""),

("md", """## 5. Run K-Means with k = 4 and read the clusters

Each cluster is named from its averages."""),
("code", """model = KMeans(n_clusters=K, n_init=20, random_state=42).fit(X)
sku["cluster"] = model.labels_

def name_of(row):
    if row["weight"] >= 4 or row["volume"] >= 30:
        return "Bulky / heavy"
    if row["season"] >= 5:
        return "Seasonal"
    if row["picks"] >= 100:
        return "Fast movers"
    return "Regular small items"

profile = sku.groupby("cluster")[FEATURES].mean().round(2)
profile.insert(0, "skus", sku.groupby("cluster").size())
profile.insert(0, "name", profile.apply(name_of, axis=1))
profile = profile.sort_values("picks", ascending=False)      # the most-picked cluster first
profile["zone"] = list("ABCDEFGH")[:K]
if profile["name"].duplicated().any():                       # two clusters that read alike keep their zone letter
    profile["name"] = profile["name"] + " " + profile["zone"]
sku["cluster_name"] = sku["cluster"].map(profile["name"])
ORDER = list(profile["name"])
COLORS = dict(zip(ORDER, ["#2a78d6", "#eda100", "#e87ba4", "#008300"]))
profile"""),

("md", """### Graph 4: how big each cluster is, and its averages

One bar per cluster. Fast movers are picked the most; bulky / heavy products are far bigger and heavier; seasonal products have the highest season index."""),
("code", """fig, axes = plt.subplots(1, 5, figsize=(17, 3.8))
panels = [("skus", "Number of SKUs")] + [(col, "Average " + LABELS[col].lower()) for col in FEATURES]
for ax, (col, title) in zip(axes, panels):
    ax.bar(range(K), profile[col], color=[COLORS[n] for n in ORDER])
    ax.set_xticks(range(K)); ax.set_xticklabels(profile["zone"]); ax.set_title(title, fontsize=10); ax.grid(axis="y", alpha=0.3)
handles = [plt.Rectangle((0, 0), 1, 1, color=COLORS[n]) for n in ORDER]
fig.legend(handles, [f"{z}: {n}" for z, n in zip(profile["zone"], ORDER)], loc="lower center", ncol=K, frameon=False)
plt.tight_layout(rect=(0, 0.08, 1, 1)); plt.show()"""),

("md", """### Graph 5: the spread inside each cluster

A box shows where the middle half of the SKUs lie. Boxes that do not overlap mean the clusters really differ on that number."""),
("code", """fig, axes = plt.subplots(1, 4, figsize=(16, 4))
for ax, col in zip(axes, FEATURES):
    boxes = ax.boxplot([sku.loc[sku["cluster_name"] == n, col] for n in ORDER], patch_artist=True)
    for box, n in zip(boxes["boxes"], ORDER):
        box.set_facecolor(COLORS[n])
    for median in boxes["medians"]:
        median.set_color("black")
    ax.set_xticks(range(1, K + 1)); ax.set_xticklabels(profile["zone"])
    if col != "season":
        ax.set_yscale("log"); plain_log(ax.yaxis)
    ax.set_title(LABELS[col]); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); plt.show()"""),

("md", """### Graph 6: the SKUs, two numbers at a time

Each dot is one SKU, coloured by its cluster."""),
("code", """pairs = [("picks", "volume"), ("picks", "season"), ("volume", "weight")]
fig, axes = plt.subplots(1, 3, figsize=(17, 4.8))
for ax, (a, b) in zip(axes, pairs):
    for n in ORDER:
        group = sku[sku["cluster_name"] == n]
        ax.scatter(group[a], group[b], s=18, alpha=0.75, color=COLORS[n], label=f"{n} ({len(group)})")
    ax.set_xscale("log"); plain_log(ax.xaxis)
    if b != "season":
        ax.set_yscale("log"); plain_log(ax.yaxis)
    ax.set_xlabel(LABELS[a]); ax.set_ylabel(LABELS[b]); ax.grid(alpha=0.3)
axes[0].legend(fontsize=8)
plt.tight_layout(); plt.show()"""),

("md", """### Graph 7: all four numbers in one picture, with PCA

PCA (also from Unit 3) squeezes the four scaled numbers into two, so every SKU can be drawn as one dot. PCA is only used to **draw** the clusters here; K-Means made them. Black crosses are the cluster centres."""),
("code", """pca = PCA(n_components=2).fit(X)
flat = pca.transform(X)
centres = pca.transform(model.cluster_centers_)
plt.figure(figsize=(7.5, 5.5))
for n in ORDER:
    mask = (sku["cluster_name"] == n).values
    plt.scatter(flat[mask, 0], flat[mask, 1], s=20, alpha=0.75, color=COLORS[n], label=n)
plt.scatter(centres[:, 0], centres[:, 1], marker="X", s=220, color="black", label="Cluster centre")
kept = 100 * pca.explained_variance_ratio_.sum()
plt.xlabel("First principal component"); plt.ylabel("Second principal component")
plt.title(f"The clusters in two dimensions (PCA keeps {kept:.0f}% of the variation)")
plt.legend(fontsize=8); plt.grid(alpha=0.3); plt.tight_layout(); plt.show()"""),

("md", """### Graph 8: a seasonal SKU against a fast mover

The most-ordered SKU of the seasonal cluster and of the fast-mover cluster, month by month. The seasonal SKU gets most of its orders in a single month; the fast mover keeps selling across many months."""),
("code", """def top_sku(cluster_name):
    group = sku[sku["cluster_name"] == cluster_name]
    return group.sort_values("picks", ascending=False).iloc[0]

wanted = [n for n in ORDER if n.startswith("Seasonal")][:1] + [n for n in ORDER if n.startswith("Fast")][:1]
if len(wanted) < 2:                                       # other data may name its clusters differently
    wanted = [profile.sort_values("season", ascending=False)["name"].iloc[0], ORDER[0]]
months = pd.period_range(by_month.index.min(), by_month.index.max(), freq="M")
plt.figure(figsize=(11, 3.8))
for n in wanted:
    row = top_sku(n)
    sold = lines[lines["product_id"] == row["product_id"]]["order_purchase_timestamp"].dt.to_period("M").value_counts()
    sold = sold.reindex(months, fill_value=0)
    plt.plot(months.astype(str), sold.values, marker="o", color=COLORS[n],
             label=f"{n}: {row['category']} ({int(row['picks'])} orders, season index {row['season']:.1f})")
plt.xticks(rotation=60, ha="right"); plt.ylabel("Orders in the month"); plt.title("Month by month: one seasonal SKU and one fast mover")
plt.legend(fontsize=8); plt.grid(alpha=0.3); plt.tight_layout(); plt.show()"""),

("md", """## 6. Clusters become zones

The most-picked cluster goes nearest to the packing desk.

**Walking distance is a simple model, not a measurement:** all SKUs share one aisle that starts at packing, each cluster takes as much of the aisle as it has SKUs, and a SKU is counted at the middle of its cluster's stretch. With no grouping, a SKU is on average half-way down the aisle."""),
("code", """AISLE = len(sku) / 3                      # metres: three SKUs for every metre of shelving
end = profile["skus"].cumsum() * AISLE / len(sku)
start = end.shift(fill_value=0)
profile["from_m"] = start.round(1)
profile["to_m"] = end.round(1)

middle = (start + end) / 2
walk_grouped = (sku["picks"] * sku["cluster"].map(middle)).sum() / sku["picks"].sum()
walk_none = AISLE / 2

print(profile[["zone", "name", "skus", "picks", "season", "volume", "weight", "from_m", "to_m"]].to_string())
print()
print(f"Walk per pick, no grouping: {walk_none:.1f} m")
print(f"Walk per pick, K-Means    : {walk_grouped:.1f} m")
print(f"Less walking in this model: {100 * (1 - walk_grouped / walk_none):.0f}%")"""),

("md", """### Graph 9: the aisle, and the walk per pick

Top: the aisle from the packing desk, split into the four zones. Bottom: the walk per pick with and without grouping, in the simple model."""),
("code", """fig, axes = plt.subplots(2, 1, figsize=(11, 4.6), gridspec_kw={"height_ratios": [1, 1.3]})
for (_, row), n in zip(profile.iterrows(), ORDER):
    axes[0].barh(0, row["to_m"] - row["from_m"], left=row["from_m"], color=COLORS[n], edgecolor="white")
    axes[0].text((row["from_m"] + row["to_m"]) / 2, 0, f"{row['zone']}\\n{int(row['skus'])} SKUs", ha="center", va="center", fontsize=9, fontweight="bold")
axes[0].set_yticks([]); axes[0].set_xlim(0, AISLE); axes[0].set_xlabel("Metres from the packing desk"); axes[0].set_title("The aisle, zone by zone")
bars = axes[1].barh(["K-Means zones", "No grouping"], [walk_grouped, walk_none], color=["#008300", "#9bbbe4"])
for bar, value in zip(bars, [walk_grouped, walk_none]):
    axes[1].text(value + 0.8, bar.get_y() + bar.get_height() / 2, f"{value:.1f} m", va="center", fontweight="bold")
axes[1].set_xlim(0, AISLE * 0.62); axes[1].set_xlabel("Walk per pick in the model (metres)"); axes[1].grid(axis="x", alpha=0.3)
plt.tight_layout(); plt.show()"""),

("md", """### Graph 10: what kind of products are in each cluster

The five most common product categories in each cluster."""),
("code", """fig, axes = plt.subplots(1, K, figsize=(17, 3.6))
for ax, n in zip(axes, ORDER):
    top = sku.loc[sku["cluster_name"] == n, "category"].value_counts().head(5)[::-1]
    ax.barh(top.index, top.values, color=COLORS[n])
    ax.set_title(n, fontsize=10); ax.set_xlabel("SKUs"); ax.grid(axis="x", alpha=0.3)
plt.tight_layout(); plt.show()"""),

("md", """## 7. Save the result

`sku_clusters.csv` appears in the Files panel on the left. It has one row for each SKU with its four numbers and its cluster."""),
("code", """out = sku[["product_id", "category"] + FEATURES + ["cluster_name"]].round(2)
out.to_csv("sku_clusters.csv", index=False)
print(len(out), "rows saved to sku_clusters.csv")
out.sort_values("picks", ascending=False).head(10)"""),

("md", """## What is real and what is a model

- The orders, sizes and weights are **real data** from Olist.
- The dataset has no field for handling needs, so **weight** stands in for it.
- The walking distance is a **simple model** of one aisle. It shows why grouping helps; it is not measured in a real warehouse.
- K-Means needs k chosen first. Here the elbow and the silhouette score both point to k = 4."""),
]

nb = {"nbformat": 4, "nbformat_minor": 5,
      "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python"}, "colab": {"name": "warehouse_sku_kmeans.ipynb", "provenance": []}},
      "cells": []}
for i, (kind, text) in enumerate(CELLS):
    src = text.split("\n"); src = [l + "\n" for l in src[:-1]] + [src[-1]]
    cell = {"cell_type": "markdown" if kind == "md" else "code", "metadata": {}, "source": src, "id": f"cell{i:02d}"}
    if kind == "code": cell.update({"execution_count": None, "outputs": []})
    nb["cells"].append(cell)
json.dump(nb, open(OUT_NB, "w"), indent=1)
with open(OUT_PY, "w") as f:
    # Every figure is saved, so the check can look at what was drawn.
    f.write("import matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as _p\n_n = [0]\n"
            "def _save(*a, **k):\n    _n[0] += 1\n    _p.savefig(f'fig-{_n[0]:02d}.png', dpi=70)\n    _p.close('all')\n_p.show = _save\n")
    for kind, text in CELLS:
        if kind == "code":
            f.write(text + "\n\n")
    f.write("print('FIGURES', _n[0])\nprint('ELBOW', [round(e, 1) for e in errors])\n")
print("wrote", OUT_NB, "and", OUT_PY, "| graphs:", sum(1 for k, t in CELLS if k == "code" and "plt.show()" in t))
