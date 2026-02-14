# STAC to DataCite OAI-AIRE Exporter

This tool converts a STAC API (SpatioTemporal Asset Catalog) into:

- DataCite-compliant JSON metadata
- OAI-PMH OpenAIRE (OAI-AIRE) XML records

It supports exporting both **collections** and **items (datasets)**.

---

## Requirements

- Python 3.9+
- requests

Install dependencies:

```bash
pip install requests
```

## Usage

```bash
python stac_to_datacite.py https://api.example.org

```
Or export a specific collection:

```bash
python stac_to_datacite.py https://api.example.org/collections/COLLECTION_ID

```
