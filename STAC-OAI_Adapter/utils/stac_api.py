import requests
from urllib.parse import urljoin

class StacApiUtils:
    def __init__(self, base_url):
        if "/collections/" in base_url:
            base_url = base_url.split("/collections/")[0]
        self.base_url = base_url.rstrip("/")

    def get_collections(self):
        r = requests.get(f"{self.base_url}/collections")
        r.raise_for_status()
        return r.json().get("collections", [])
    
    def get_collection(self, collection_id):
        r = requests.get(f"{self.base_url}/collections/{collection_id}")
        r.raise_for_status()
        return r.json()

    def get_items(self, collection_id, limit=None):
        items = []
        url = f"{self.base_url}/collections/{collection_id}/items"

        while url:
            r = requests.get(url)
            r.raise_for_status()
            data = r.json()

            for item in data.get("features", []):
                items.append(item)
                if limit and len(items) >= limit:
                    return items

            url = next(
                (l["href"] for l in data.get("links", []) if l.get("rel") == "next"),
                None
            )

        return items

