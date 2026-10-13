# Where the data comes from

**Brazilian E-Commerce Public Dataset by Olist**

- Source: https://github.com/olist/work-at-olist-data (folder `datasets/`)
- Licence: MIT
- What it is: 99,441 real orders placed on the Olist marketplace in Brazil between September 2016 and October 2018, with 112,650 order lines for 32,951 products. Customers and sellers are anonymised, and products have a category but no name.

## Files the notebook reads, live from the source

| File | Size | What we use from it |
|---|---|---|
| `olist_order_items_dataset.csv` | 15.0 MB | one row each time a product was ordered (`order_id`, `product_id`) |
| `olist_orders_dataset.csv` | 17.7 MB | when each order was placed (`order_purchase_timestamp`) |
| `olist_products_dataset.csv` | 2.4 MB | weight and size of each product (`product_weight_g`, `product_length_cm`, `product_height_cm`, `product_width_cm`) |
| `product_category_name_translation.csv` | 3 KB | category names in English |

The raw files are not copied into this repository. The notebook downloads them from the source each time it runs.

## What is in this folder

- `sku_features.csv`: the 383 products ordered at least 30 times, with the four numbers built from the source (`picks`, `season`, `volume`, `weight`) and the cluster K-Means gave each one. `sku` is the first 8 characters of Olist's `product_id`.
- `results.json`: the elbow values, the four clusters and the walking-model figures that the web page and the slides show.

## How each number is built

| Number | Meaning | Built from |
|---|---|---|
| `picks` | pick frequency | count of order lines for the product |
| `season` | seasonal demand | share of its orders in its busiest calendar month, times 12 |
| `volume` | physical size, litres | length x height x width / 1000 |
| `weight` | handling, kg | product weight / 1000 |

The dataset has no field for handling needs, so weight stands in for it.
