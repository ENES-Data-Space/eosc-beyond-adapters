import os
import sys
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.stac_api import StacApiUtils
from utils.datacite_utils import DataciteExportXML, prettify_xml

EXPORT_JSON_DIR = "./exports"
EXPORT_XML_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "oai_aire_records")
MAX_WORKERS = 8


def stac_to_datacite(collection, items=None):
    creation_date = collection.get("creation_date")
    pub_year = None
    if creation_date:
        try:
            pub_year = datetime.fromisoformat(creation_date.replace("Z", "")).year
        except Exception:
            pass

    related = []
    if items:
        for item in items:
            related.append({
                "relatedIdentifier": f"{collection['id']}/items/{item['id']}",
                "relatedIdentifierType": "URL",
                "relationType": "HasPart"
            })

    creators = [{"creatorName": p.get("name", "Unknown")} for p in collection.get("providers", [])] \
        or [{"creatorName": collection.get("cmip6:institution", collection.get("cmip6:institution_id", "Unknown"))}]

    return {
        "identifier": {"identifier": f"{collection.get('id')}", "identifierType": "URL"},
        "creators": creators,
        "titles": [{"title": collection.get("title", "No Title")}],
        "publisher": collection.get("institution_id", "CMCC"),
        "publicationYear": pub_year,
        "resourceType": {"resourceTypeGeneral": "Collection", "resourceType": "Data Collection"},
        "descriptions": [{"description": collection.get("description", ""), "descriptionType": "Abstract"}],
        "subjects": [{"subject": k} for k in collection.get("keywords", [])],
        "relatedIdentifiers": related
    }

def stac_item_to_datacite(item):
    props = item.get("properties", {})
    assets = item.get("assets", {})
    links = item.get("links", [])

    col_id = item.get('collection')
    item_id = item.get('id')
    identifier_val = f"https://catalogue.eneslab.pilot.eosc-beyond.eu/collections/{col_id}/items/{item_id}"
    identifier_type = "URL"

    creation_date = props.get("creation_date") or props.get("datetime")
    pub_year = None
    if creation_date:
        try:
            pub_year = datetime.fromisoformat(creation_date.replace("Z", "")).year
        except Exception:
            pass

    creators = []
    if props.get("contact"):
        creators.append({
            "creatorName": props["contact"],
            "affiliation": props.get("cmip6:institution_id", "None")
        })

    titles = [{"title": item.get("id")}]
    publisher = props.get("cmip6:institution_id", "None")
    license = "Creative Commons Attribution-ShareAlike"

    subjects = [{"subject": props[k]} for k in [
        "cmip6:mip_era","cmip6:activity_id","cmip6:institution_id","cmip6:source_id",
        "cmip6:experiment_id", "cmip6:variant_label", "cmip6:table_id", "cmip6:variable_id", "cmip6:realm"
    ] if props.get(k)]

    dates = [{"date": creation_date, "dateType": "Issued"}] if creation_date else []
    language = "eng"

    resource_type = {
        "resourceTypeGeneral": "dataset",
        "uri": "http://purl.org/coar/resource_type/c_ddb1",
        "resourceType": "dataset"
    }

    alternate_identifiers = [{"alternateIdentifier": item.get("id"), "alternateIdentifierType": "STAC-ID"}]
    contributor = "CMCC"

    related = []
    for asset in assets.values():
        if asset.get("href"):
            related.append({"relatedIdentifier": asset["href"], "relatedIdentifierType": "URL", "relationType": "HasPart"})
    if props.get("cmip6:further_info_url"):
        related.append({"relatedIdentifier": props["cmip6:further_info_url"], "relatedIdentifierType": "URL", "relationType": "IsDescribedBy"})
    for l in links:
        if l.get("href"):
            rel = l.get("rel", "related")
            relationType = "IsMetadataFor" if rel=="self" else "IsPartOf" if rel=="collection" else "Related"
            related.append({"relatedIdentifier": l["href"], "relatedIdentifierType": "URL", "relationType": relationType})

    if item.get("collection"):
        related.append({"relatedIdentifier": item["collection"], "relatedIdentifierType": "Local", "relationType": "IsPartOf"})

    formats = [a["type"] for a in assets.values() if a.get("type")]

    version = {"uri":"http://purl.org/coar/version/c_970fb48d4fbd8a85","version":"VoR"}
    rights_list = {"rightsURI":"http://purl.org/coar/access_right/c_abf2","rights":"open access"}
    fundingReferences = [{
        "funderName": "European Commission",
        "funderIdentifier": "http://doi.org/10.13039/100018693",
        "funderIdentifierType": "Crossref Funder ID",
        "fundingStream": "HORIZON EUROPE Framework Programme",
        "awardNumber": {"awardURI": "https://cordis.europa.eu/project/id/101131875","awardNumber": "101131875"},
        "awardTitle": "EOSC Beyond: advancing innovation and collaboration for research"
    }]

    descriptions = []
    if props.get("cmip6:experiment"):
        descriptions.append({"description": props.get("cmip6:experiment")})
    if props.get("description"):
        descriptions.append({"description": props.get("description")})

    geo_locations = []
    if "bbox" in item and len(item["bbox"])==4:
        bbox = item["bbox"]
        geo_locations.append({"geoLocationBox":{"westBoundLongitude":bbox[0],"southBoundLatitude":bbox[1],"eastBoundLongitude":bbox[2],"northBoundLatitude":bbox[3]}})

    return {
        "identifier": {"identifier": identifier_val, "identifierType": identifier_type},
        "creators": creators,
        "titles": titles,
        "publisher": publisher,
        "publicationYear": str(pub_year) if pub_year else None,
        "subjects": subjects,
        "dates": dates,
        "language": language,
        "resourceType": resource_type,
        "alternateIdentifiers": alternate_identifiers,
        "relatedIdentifiers": related,
        "formats": formats,
        "version": version,
        "rightsList": rights_list,
        "descriptions": descriptions,
        "geoLocations": geo_locations,
        "fundingReferences": fundingReferences,
        "contributor": contributor,
        "license": license
    }

def extract_id(data: dict) -> str:
    if data.get("id"):
        return data["id"]
    titles = data.get("titles")
    if isinstance(titles, str):
        return titles.replace(".", "_")
    if isinstance(titles, list) and titles:
        title = titles[0].get("title")
        if title:
            return title.replace(".", "_")
    return ""

def export_datacite(enteries, mapper, label, subdir=None):
    target_dir = os.path.join(EXPORT_JSON_DIR, label)
    if subdir:
        target_dir = os.path.join(target_dir, subdir)
    os.makedirs(target_dir, exist_ok=True)
    for entry in enteries:
        data = entry[1] if isinstance(entry, tuple) else entry
        datacite_json = mapper(data)
        id_ = extract_id(data)
        if id_:
            output = os.path.join(target_dir, f"{id_}.json")
            with open(output, "w") as f:
                json.dump(datacite_json, f, indent=2)


def fetch_items_for_collection(api, col):
    items = api.get_items(col["id"])
    print(f"{col['id']}: fetched {len(items)} items")
    return col, items

def main():
    if len(sys.argv) < 2:
        print("Usage: python stac_to_datacite_parallel.py <STAC catalog URL>")
        sys.exit(1)

    catalog_url = sys.argv[1]
    print("Fetching catalog from:", catalog_url)
    api = StacApiUtils(catalog_url)
    collections = api.get_collections()
    if not collections:
        print("No collections found!")
        sys.exit(0)
    print(f"Found {len(collections)} collections")

    all_items = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_items_for_collection, api, col): col for col in collections}
        for future in as_completed(futures):
            col, items = future.result()
            all_items[col["id"]] = items

    for col in collections:
        col_id = col["id"]
        items = all_items.get(col_id, [])
        print(f"Processing collection: {col_id} with {len(items)} items")

        if items:
            datacite_items = [stac_item_to_datacite(item) for item in items]
            export_datacite(datacite_items, lambda x: x, "item", subdir=col_id)
            DataciteExportXML.export_oai_aire(datacite_items, EXPORT_XML_DIR)

        col_json = stac_to_datacite(col, items=items)
        export_datacite([col_json], lambda x: x, "collection")
        DataciteExportXML.export_oai_aire([col_json], EXPORT_XML_DIR)

    print("Datacite export complete!")

if __name__ == "__main__":
    main()
