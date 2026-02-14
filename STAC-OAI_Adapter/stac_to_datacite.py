#python stac_to_datacite.py https://api.eneslab.pilot.eosc-beyond.eu/collections/CMIP_S3  
import os
import sys
import re
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.stac_api import StacApiUtils
from utils.datacite_utils import DataciteExportXML

EXPORT_JSON_DIR = "./exports"
EXPORT_XML_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "oai_aire_records")
MAX_WORKERS = 8


def safe_year(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "")).year
    except Exception:
        return None


def safe_filename(value: str, max_len=150) -> str:
    value = value.strip()
    value = re.sub(r'[<>:"/\\|?*]', '_', value)
    value = re.sub(r'\s+', '_', value)
    return value[:max_len]


def extract_id(data: dict, is_item=False) -> str:
    if is_item:
        if "id" in data:
            return data["id"]
        ident = data.get("identifier", {}).get("identifier", "")
        return ident.split("/")[-1] if ident else "record"

    if "id" in data:
        return data["id"]
    return "record"



def stac_collection_to_datacite(collection, base_url, items=None):
    pub_year = safe_year(collection.get("creation_date"))

    creators = (
        [{"creatorName": p.get("name", "Unknown")} for p in collection.get("providers", [])]
        or [{"creatorName": collection.get("cmip6:institution_id", "Unknown")}]
    )

    related = []
    if items:
        for item in items:
            related.append({
                "relatedIdentifier": f"{base_url}/collections/{collection['id']}/items/{item['id']}",
                "relatedIdentifierType": "URL",
                "relationType": "HasPart"
            })

    return {
        "identifier": {
            "identifier": f"{base_url}/collections/{collection['id']}",
            "identifierType": "URL"
        },
        "creators": creators,
        "titles": [{"title": collection.get("title", collection["id"])}],
        "publisher": collection.get("institution_id", "CMCC"),
        "publicationYear": pub_year,
        "resourceType": {
            "resourceTypeGeneral": "Collection",
            "resourceType": "Data Collection"
        },
        "descriptions": [{
            "description": collection.get("description", ""),
            "descriptionType": "Abstract"
        }],
        "subjects": [{"subject": k} for k in collection.get("keywords", [])],
        "relatedIdentifiers": related
    }


def stac_item_to_datacite(item, base_url):
    props = item.get("properties", {})
    assets = item.get("assets", {})
    links = item.get("links", [])

    col_id = item["collection"]
    item_id = item["id"]
    pub_year = safe_year(props.get("creation_date") or props.get("datetime"))

    creators = []
    if props.get("contact"):
        creators.append({
            "creatorName": props["contact"],
            "affiliation": props.get("cmip6:institution_id")
        })

    subjects = [
        {"subject": props[k]}
        for k in [
            "cmip6:mip_era", "cmip6:activity_id", "cmip6:institution_id",
            "cmip6:source_id", "cmip6:experiment_id", "cmip6:variant_label",
            "cmip6:table_id", "cmip6:variable_id", "cmip6:realm"
        ]
        if props.get(k)
    ]

    related = []
    for asset in assets.values():
        if asset.get("href"):
            related.append({
                "relatedIdentifier": asset["href"],
                "relatedIdentifierType": "URL",
                "relationType": "HasPart"
            })
    for link in links:
        if link.get("href"):
            rel = link.get("rel")
            relation_type = (
                "IsMetadataFor" if rel == "self"
                else "IsPartOf" if rel == "collection"
                else "Related"
            )
            related.append({
                "relatedIdentifier": link["href"],
                "relatedIdentifierType": "URL",
                "relationType": relation_type
            })
    related.append({
        "relatedIdentifier": f"{base_url}/collections/{col_id}",
        "relatedIdentifierType": "URL",
        "relationType": "IsPartOf"
    })

    return {
        "identifier": {
            "identifier": f"{base_url}/collections/{col_id}/items/{item_id}",
            "identifierType": "URL"
        },
        "creators": creators,
        "titles": [{"title": item_id}],
        "publisher": props.get("cmip6:institution_id", "CMCC"),
        "publicationYear": pub_year,
        "subjects": subjects,
        "language": "eng",
        "resourceType": {
            "resourceTypeGeneral": "Dataset",
            "resourceType": "Dataset",
            "uri": "http://purl.org/coar/resource_type/c_ddb1"
        },
        "alternateIdentifiers": [{
            "alternateIdentifier": item_id,
            "alternateIdentifierType": "STAC-ID"
        }],
        "relatedIdentifiers": related,
        "formats": [a["type"] for a in assets.values() if a.get("type")],
        "rightsList": {
            "rights": "open access",
            "rightsURI": "http://purl.org/coar/access_right/c_abf2"
        },
        "descriptions": [{"description": props.get("description", "")}],
        "fundingReferences": [{
            "funderName": "European Commission",
            "funderIdentifier": "http://doi.org/10.13039/100018693",
            "funderIdentifierType": "Crossref Funder ID",
            "awardNumber": {
                "awardURI": "https://cordis.europa.eu/project/id/101131875",
                "awardNumber": "101131875"
            },
            "awardTitle": "EOSC Beyond"
        }]
    }


def export_json(records, label, subdir=None, is_item=False):
    target = os.path.join(EXPORT_JSON_DIR, label)
    if subdir:
        target = os.path.join(target, subdir)
    os.makedirs(target, exist_ok=True)

    for rec in records:
        rec_id = extract_id(rec, is_item=is_item)
        path = os.path.join(target, f"{rec_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=2)


def fetch_items(api, collection):
    items = api.get_items(collection["id"])
    print(f"{collection['id']}: {len(items)} items")
    return collection, items


def main():
    if len(sys.argv) < 2:
        print("Usage: python stac_to_datacite.py <STAC URL>")
        sys.exit(1)

    input_url = sys.argv[1]
    print("Fetching:", input_url)

    api = StacApiUtils(input_url)
    collections = api.get_collections()

    if "/collections/" in input_url:
        match = re.match(r"(.*)/collections/?([^/]*)", input_url)
        if not match:
            print("Invalid collection URL")
            sys.exit(1)

        base_url, collection_id = match.groups()

        api = StacApiUtils(base_url)
        collections = api.get_collections()

        if collection_id:
            collections = [c for c in collections if c["id"] == collection_id]

            if not collections:
                print(f"Collection {collection_id} not found")
                sys.exit(1)


    all_items = {}
    if len(collections) > 1:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(fetch_items, api, col) for col in collections]
            for future in as_completed(futures):
                try:
                    col, items = future.result()
                    all_items[col["id"]] = items
                except Exception as e:
                    print(f"Error fetching items for collection {col['id']}: {e}")
    

    else:
        col = collections[0]
        all_items[col["id"]] = api.get_items(col["id"])

    for col in collections:
        items = all_items[col["id"]]
        if not items:
            print(f"Collection {col['id']} has no items, skipping item export")
            continue

        item_dc = [stac_item_to_datacite(i, api.base_url) for i in items]
        col_dc = stac_collection_to_datacite(col, api.base_url, items)

        if item_dc:
            export_json(item_dc, "items", col["id"], is_item=True)
            DataciteExportXML.export_oai_aire(item_dc, EXPORT_XML_DIR)

        export_json([col_dc], "collections")
        DataciteExportXML.export_oai_aire([col_dc], EXPORT_XML_DIR)

    print("Datacite export complete")


if __name__ == "__main__":
    main()
