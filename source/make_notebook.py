"""Write the Colab notebook, and the same code as one plain script for checking it runs."""
import json, sys

OUT_NB, OUT_PY = sys.argv[1], sys.argv[2]

CELLS = [
("md", """# Grouping warehouse products with K-Means clustering

Machine Learning (21CSC305P), Project Review 3, Team Cash guard.

This notebook reads a **real, public dataset straight from the internet**, builds four numbers for every product (SKU), groups the SKUs with **K-Means**, and gives each group a place in the warehouse.

**Data:** the Brazilian e-commerce dataset published by Olist: about 99,000 orders placed between 2016 and 2018.
Live link: https://github.com/olist/work-at-olist-data (MIT licence).

Run every cell from top to bottom: **Runtime > Run all**."""),

("md", """## 1. Read the data from the live link"""),
("code", """import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

BASE = "https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets/"
products = pd.read_csv(BASE + "olist_products_dataset.csv")        # size and weight of every product
items = pd.read_csv(BASE + "olist_order_items_dataset.csv")        # one row each time a product was ordered
orders = pd.read_csv(BASE + "olist_orders_dataset.csv", parse_dates=["order_purchase_timestamp"])
names = pd.read_csv(BASE + "product_category_name_translation.csv")  # category names in English

print(f"{len(orders):,} orders, {len(items):,} order lines, {items['product_id'].nunique():,} products")
print("from", orders["order_purchase_timestamp"].min().date(), "to", orders["order_purchase_timestamp"].max().date())"""),

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

plt.figure(figsize=(6, 4))
plt.plot(ks, errors, marker="o")
plt.xlabel("Number of clusters (k)"); plt.ylabel("Within-cluster variance"); plt.title("Elbow curve on the real data")
plt.grid(alpha=0.3); plt.show()

for k in ks:
    drop = "" if k == 1 else f"  {100 * (1 - errors[k - 1] / errors[k - 2]):.0f}% lower than k = {k - 1}"
    score = "" if k == 1 else f"  silhouette {silhouettes[k]:.3f}"
    print(f"k = {k}: error {errors[k - 1]:7.1f}{drop}{score}")"""),

("md", """## 5. Run K-Means with k = 4 and read the clusters

Each cluster is named from its averages."""),
("code", """K = 4
model = KMeans(n_clusters=K, n_init=20, random_state=42).fit(X)
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
profile"""),

("md", """## 6. Clusters become zones

The most-picked cluster goes nearest to the packing desk.

**Walking distance is a simple model, not a measurement:** all SKUs share one aisle that starts at packing, each cluster takes as much of the aisle as it has SKUs, and a SKU is counted at the middle of its cluster's stretch. With no grouping, a SKU is on average half-way down the aisle."""),
("code", """AISLE = len(sku) / 3                      # metres: three SKUs for every metre of shelving
end = profile["skus"].cumsum() * AISLE / len(sku)
start = end.shift(fill_value=0)
profile["zone"] = list("ABCDEFGH")[:K]
profile["from_m"] = start.round(1)
profile["to_m"] = end.round(1)

middle = (start + end) / 2
walk_grouped = (sku["picks"] * sku["cluster"].map(middle)).sum() / sku["picks"].sum()
walk_none = AISLE / 2

print(profile[["name", "skus", "picks", "season", "volume", "weight", "zone", "from_m", "to_m"]].to_string())
print()
print(f"Walk per pick, no grouping: {walk_none:.1f} m")
print(f"Walk per pick, K-Means    : {walk_grouped:.1f} m")
print(f"Less walking in this model: {100 * (1 - walk_grouped / walk_none):.0f}%")"""),

("md", """## 7. See the clusters"""),
("code", """sku["cluster_name"] = sku["cluster"].map(profile["name"])
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
for name, group in sku.groupby("cluster_name"):
    axes[0].scatter(group["picks"], group["volume"], s=18, alpha=0.75, label=f"{name} ({len(group)})")
    axes[1].scatter(group["picks"], group["season"], s=18, alpha=0.75, label=name)
axes[0].set_xscale("log"); axes[0].set_yscale("log")
axes[0].set_xlabel("Picks (order lines)"); axes[0].set_ylabel("Volume (litres)"); axes[0].set_title("Size against pick frequency")
axes[1].set_xscale("log")
axes[1].set_xlabel("Picks (order lines)"); axes[1].set_ylabel("Season index"); axes[1].set_title("Seasonality against pick frequency")
axes[0].legend(fontsize=8); plt.tight_layout(); plt.show()"""),

("md", """## 8. Save the result

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
    f.write("import matplotlib\nmatplotlib.use('Agg')\n")
    for kind, text in CELLS:
        if kind == "code":
            f.write(text + "\n\n")
    f.write("print('ELBOW', [round(e, 1) for e in errors])\nprint('SIL', {k: round(v, 3) for k, v in silhouettes.items()})\n")
print("wrote", OUT_NB, "and", OUT_PY)
