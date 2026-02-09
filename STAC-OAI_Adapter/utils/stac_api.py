import requests
from urllib.parse import urljoin

class StacApiUtils:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")

    def get_collections(self):
        r = requests.get(f"{self.base_url}/collections")
        r.raise_for_status()
        return r.json().get("collections", [])

    def get_items(self, collection_id):
        items = []
        url = f"{self.base_url}/collections/{collection_id}/items"

        while url:
            r = requests.get(url)
            r.raise_for_status()
            data = r.json()

            for item in data.get("features", []):
                item["collection"] = collection_id
                items.append(item)

            url = next(
                (l["href"] for l in data.get("links", []) if l.get("rel") == "next"),
                None
            )

        return items
