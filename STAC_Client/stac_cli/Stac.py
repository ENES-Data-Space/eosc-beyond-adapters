import requests
import logging

class STAC :
    def __init__(self, base_url:str, token:str | None = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

        self.logger = logging.getLogger("stac-client")

        if token:
            self.session.headers.update({
                 "Authorization": f"Bearer {token}"
            })
        self.session.headers.update({
            "Content-Type": "application/json"
        })

    def _request(self, Method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"
        self.logger.info(f"{Method} {url}")

        response = self.session.request(Method, url, **kwargs)

        try:
            data = response.json()
        except ValueError:
            data = {"detail": [{"msg": response.text}]}

        return data



    def getcollections(self):
        data = self._request("GET","/collections")
        collections = data.get("collections",[])
        return [c.get("id") for c in collections if "id" in c]
    
    
    def getcollection(self, collection_id: str):
        return self._request("GET",f"/collections/{collection_id}")
    
    def get_items(self, collection_id: str,limit=1000): 
        data = self._request("GET", f"/collections/{collection_id}/items?limit={limit}")
        items = data.get("features",[])
        return [item.get("id") for item in items if "id" in item]
    
    def add_item(self,collection_id,item: dict):
        return self._request( "POST", f"/collections/{collection_id}/items", json=item )
    
    def get_item(self, collection_id, item_id):
        return self._request("GET",f"/collections/{collection_id}/items/{item_id}")
    

    def verify_token(self,token:str) -> bool:
        try:
            data = self._request("GET","/auth/realms/egi/protocol/openid-connect/userinfo",headers = {"Authorization": f"Bearer {token}",
    "Content-type": "application/json"})
            print(data)
            response = data.get("email_verified")

            if response:
                return True
            else :
                return False
        except Exception:
            return False