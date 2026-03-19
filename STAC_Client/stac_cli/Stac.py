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

    def _request(self,Method : str , endpoint:str, **kwargs):
        url = f'{self.base_url}{endpoint}'
        self.logger.info(f"{Method} {url}")
        respond = self.session.request(Method,url,**kwargs)

        if not respond.ok:
            self.logger.error(respond.text)
            respond.raise_for_status()
        else:
            return respond.json()

        return None


    def getcollections(self):
        return self._request("GET","/collections")
    
    def getcollection(self, collection_id: str):
        return self._request("GET",f"/collection/{collection_id}")
    
    def get_items(self, collection_id: str): 
        return self._request("GET", f"/collections/{collection_id}/items")
    
    def add_item(self,collection_id,item: dict):
        return self._request( "POST", f"/collections/{collection_id}/items", json=item )