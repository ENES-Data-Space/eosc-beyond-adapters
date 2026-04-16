# STAC Client CLI

A command-line tool for interacting with a STAC (SpatioTemporal Asset Catalog) API.

---

## Installation

Clone the repository and install in editable mode:

```bash
pip install -e .
```

This will make the `stac_cli` command available in your terminal.

---

## Usage

```bash
stac_cli <command> <subcommand> [options]
```

---

## Commands

### Collections

Get all collections:

```bash
stac_cli collections get
```

Get a specific collection:

```bash
stac_cli collections get --collection_id CMIP_S3
```

---

### Items

Get all items in a collection:

```bash
stac_cli items get --collection_id CMIP_S3
```

Get a specific item:

```bash
stac_cli items get --collection_id CMIP_S3 --item_id <ITEM_ID>
```

Add a new item:

```bash
stac_cli items add \
  --collection_id shared_collection \
  --token <TOKEN> or $TOEKN\
  --file item.json
```

---

### Authentication

Verify a token:

```bash
stac_cli auth verify --token <TOKEN> or $TOEKN
```

Returns `SUCCESS` or `FAIL`.

---

### Template

Generate a STAC item template:

```bash
stac_cli items create_template
```

---

## Notes

* Input files must be valid JSON
* Assets must include a valid `href` (URL)
* Geometry must follow GeoJSON format
* A valid token is required for adding items
