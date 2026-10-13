# Grouping warehouse products with K-Means clustering

A student project for Machine Learning (21CSC305P), Project Review 3, by Team Cash guard.

**Live demo:** https://zanyanbu.github.io/warehouse-sku-kmeans/

## The problem

Partition warehouse product SKUs by pick frequency, seasonal demand, physical size and handling needs, so that managers can place inventory smartly and workers walk less while picking orders.

From the solutions in Unit 3 (K-Means, mixtures of Gaussians, hierarchical clustering, PCA and factor analysis) we selected **K-Means clustering**: the task is a partition, every SKU needs exactly one storage zone, and K-Means stays simple and fast for thousands of SKUs.

## What the live demo shows

- **Run K-Means yourself.** 120 example SKUs, one round at a time: assign every SKU to the nearest centre, move the centres, repeat until nothing changes.
- **Elbow chart.** The error (within-cluster variance) for k = 1 to 8, to choose k.
- **See it on the shelves.** The same products on the racks of one aisle. Choose a solution (no grouping, K-Means, hierarchical clustering, mixture of Gaussians, PCA) and watch the products move.
- **Clusters become zones.** Each cluster is read from its averages and given a place, the most-picked one nearest to packing.

Everything runs in the browser from one file, `index.html`. There is nothing to install and no server.

## What is real and what is an example

- The data is **made up in the browser**. No real warehouse data is used.
- "Walk per pick" is a **simple model, not a measurement**: all SKUs share one 40 m aisle, the most-picked group takes the stretch nearest to packing, and each group takes as much of the aisle as it has products.
- The first start of each K-Means run is picked to show the steps clearly. "New starting centres" is a plain random start, and can get stuck in a worse grouping. That is a known limit of K-Means, and the page says so when it happens.
- The numbers in the slides are a separate small example. They show the method, not results.

## What is in this repository

| Path | What it is |
|---|---|
| `index.html` | The live demo (plain HTML, CSS and JavaScript) |
| `slides/kmeans-sku-clustering.pptx` | The 12-slide presentation |
| `script/presentation-script.pdf` | The presentation script: 4 speakers, 3 slides each, with simple examples and terms |
| `source/build_deck.js` | The script that generated the slides (needs `pptxgenjs`) |
| `source/build_script.py` | The script that generated the presentation script (needs `reportlab`) |

The two build scripts are kept for reference. They expect the slide pictures and a logo file beside them, which are not in this repository.

## Run it on your own computer

Open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.
