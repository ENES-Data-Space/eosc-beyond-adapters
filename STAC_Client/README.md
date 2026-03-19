# STAC Client CLI

A lightweight Python client and CLI tool to interact with a **STAC (SpatioTemporal Asset Catalog) API**.

This project provides:

* A reusable **STAC API client**
* A **command-line interface (CLI)**
* A **template generator** for creating valid STAC items

---

## Features

*  List available collections
*  Retrieve items from a collection
*  Add new items (authenticated)
*  Validate STAC items before upload
*  Token-based authentication (Bearer)    

---

##  Project Structure

```text
STAC_Client/
│
├── stac_cli/
│   ├── __init__.py
│   ├── stac.py        # STAC API client
│   ├── cli.py         # CLI commands
│   ├── models.py      # Pydantic models
│   └── template.py    # Item generator
│
├── requirements.txt
└── README.md
```

---

##  Requirements

* Python 3.10+
* STAC API running

Install dependencies:

```bash
pip install -r requirements.txt
```

---

##  Usage

Run CLI commands using:

```bash
python -m stac_cli.cli <command>
```

---

##  Commands

### 1. List Collections

```bash
python -m stac_cli.cli collections
```

 Fetch all available STAC collections.

---

### 2. List Items in a Collection

```bash
python -m stac_cli.cli items <collection_id>
```

 Example:

```bash
python -m stac_cli.cli items shared_collection
```

---

### 3. Add Item to `shared_collection`

```bash
python -m stac_cli.cli add-item \
--token <TOKEN> \
--id <ITEM_ID> \
--lon <LONGITUDE> \
--lat <LATITUDE> \
--asset <ASSET_URL> \
--description "<DESCRIPTION>"
```

 Example:

```bash
python -m stac_cli.cli add-item \
--token eyJhbGciOi... \
--id test-item \
--lon 12.49 \
--lat 41.89 \
--asset https://example.com/data.tif \
--description "Test upload"
```

---

##  Authentication

* Required only for **adding items**
* Token is passed via:

```bash
--token <TOKEN>
```

* Automatically included in request headers:

```text
Authorization: Bearer <TOKEN>
```

---

##  Template & Validation

When adding an item:

1. A STAC item is generated using a template
2. The item is validated using **Pydantic models**
3. Invalid data raises an error before sending the request

---

##  API Endpoints Used

| Operation       | Method | Endpoint                               |
| --------------- | ------ | -------------------------------------- |
| Get collections | GET    | `/collections`                         |
| Get items       | GET    | `/collections/{collection_id}/items`   |
| Add item        | POST   | `/collections/shared_collection/items` |


---

##  Development

Run locally:

```bash
python -m stac_cli.cli collections
```

---
